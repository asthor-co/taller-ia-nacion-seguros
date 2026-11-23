"""Step 06 — Evalúa tu asistente contra el banco de preguntas.

Uso:
    python steps/step-06/evaluar.py                                  # puntaje base
    python steps/step-06/evaluar.py --variante "k=3" --args "--k 3"  # una variante de tu tarjeta
    python steps/step-06/evaluar.py --rapido                         # 20 preguntas (si falta tiempo)
    python steps/step-06/evaluar.py --seguridad                      # suma las preguntas de seguridad (step 07)

Métricas:
    acierto              la respuesta coincide con la esperada (la juzga otro modelo: LLM como juez)
    cita correcta        cita al menos una de las cláusulas correctas (se verifica sin modelo)
    abstención correcta  ante preguntas fuera de la póliza, dice que no sabe

El asistente se llama por su contrato: python mi-asistente/asistente.py --json "pregunta".
Para otra ruta, definí ASISTENTE_CMD (por ejemplo: ASISTENTE_CMD="python checkpoints/step-06/asistente.py").
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shlex
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.markup import escape
from rich.table import Table

RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")

JUEZ = "claude-sonnet-5-5"
PRECIO_JUEZ = (2.00, 10.00)  # USD por millón de tokens (entrada, salida)
consola = Console()

ESQUEMA_JUEZ = {
    "type": "object",
    "properties": {
        "correcta": {"type": "boolean"},
        "motivo": {"type": "string"},
    },
    "required": ["correcta", "motivo"],
    "additionalProperties": False,
}

PROMPT_JUEZ = """Sos un evaluador estricto de un asistente de seguros. Compará la respuesta del asistente con la respuesta esperada.

La respuesta es correcta si el veredicto coincide (cubre / no_cubre / depende) y si no contradice ni omite la condición, el límite o el plazo central de la respuesta esperada. No importa la redacción ni el largo. Si el asistente agrega información correcta, no la penalices; si agrega una afirmación falsa relevante, es incorrecta.

Pregunta: {pregunta}

Respuesta esperada (veredicto: {veredicto_esperado}): {respuesta_esperada}

Respuesta del asistente (veredicto: {veredicto}): {respuesta}

Devolvé correcta (true/false) y un motivo de una oración."""


def comando_asistente(extra: str) -> list[str]:
    base = shlex.split(os.environ["ASISTENTE_CMD"], posix=os.name != "nt") if os.environ.get("ASISTENTE_CMD") else [
        sys.executable, str(RAIZ / "mi-asistente" / "asistente.py")]
    return [*base, *shlex.split(extra, posix=os.name != "nt")]


def normalizar(clausula: str) -> str:
    m = re.search(r"(\d+)", clausula or "")
    return f"Art. {int(m.group(1))}" if m else (clausula or "").strip()


def preguntar(cmd: list[str], pregunta: str) -> dict:
    try:
        p = subprocess.run([*cmd, "--json", pregunta], capture_output=True, text=True, timeout=240,
                           cwd=RAIZ, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
        if p.returncode != 0:
            return {"error": p.stderr.strip()[-300:] or "el asistente terminó con error"}
        datos = json.loads(p.stdout)
        return datos if isinstance(datos, dict) else {"error": "la salida no es un objeto JSON"}
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except json.JSONDecodeError:
        return {"error": "la salida no es JSON"}


def juzgar(cliente: anthropic.Anthropic, item: dict, datos: dict) -> tuple[bool, str, float]:
    prompt = PROMPT_JUEZ.format(veredicto=datos.get("veredicto"), respuesta=datos.get("respuesta", ""), **item)
    for intento in range(4):
        try:
            r = cliente.messages.create(
                model=JUEZ, max_tokens=8000,
                output_config={"effort": "low", "format": {"type": "json_schema", "schema": ESQUEMA_JUEZ}},
                messages=[{"role": "user", "content": prompt}],
            )
            costo = (r.usage.input_tokens * PRECIO_JUEZ[0] + r.usage.output_tokens * PRECIO_JUEZ[1]) / 1_000_000
            if r.stop_reason in ("refusal", "max_tokens"):
                return False, f"el juez no pudo decidir ({r.stop_reason})", costo
            veredicto = json.loads("".join(b.text for b in r.content if b.type == "text"))
            return bool(veredicto["correcta"]), str(veredicto["motivo"]), costo
        except (anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError,
                anthropic.APITimeoutError):
            time.sleep(2 ** intento * 3)
        except (anthropic.APIStatusError, ValueError, KeyError) as e:
            return False, f"error del juez: {type(e).__name__}", 0.0
    return False, "el juez no respondió", 0.0


def evaluar_item(cmd: list[str], cliente: anthropic.Anthropic, item: dict) -> dict:
    try:
        return _evaluar_item(cmd, cliente, item)
    except Exception as e:  # una pregunta rota no puede tirar abajo toda la evaluación
        return {"id": item["id"], "tipo": item["tipo"], "pregunta": item["pregunta"], "salida": {}, "costo_usd": 0.0,
                "acierto": None if item["debe_abstenerse"] else False, "cita_correcta": None if item["debe_abstenerse"] else False,
                "abstencion_correcta": False if item["debe_abstenerse"] else None, "motivo": f"error inesperado: {type(e).__name__}"}


def _evaluar_item(cmd: list[str], cliente: anthropic.Anthropic, item: dict) -> dict:
    datos = preguntar(cmd, item["pregunta"])
    r = {"id": item["id"], "tipo": item["tipo"], "pregunta": item["pregunta"], "salida": datos,
         "costo_usd": (datos.get("uso") or {}).get("costo_usd", 0.0)}
    if "error" in datos:
        if item["debe_abstenerse"]:
            r.update(acierto=None, cita_correcta=None, abstencion_correcta=False)
        else:
            r.update(acierto=False, cita_correcta=False, abstencion_correcta=None)
        r["motivo"] = f"error: {datos['error']}"
        return r
    abstuvo = bool(datos.get("abstencion")) or datos.get("veredicto") == "no_sabe"
    if item["debe_abstenerse"]:
        r.update(acierto=None, cita_correcta=None, abstencion_correcta=abstuvo,
                 motivo="se abstuvo" if abstuvo else "respondió algo que no está en las pólizas")
        return r
    citadas = {f"{(c.get('documento') or '').lower()}#{normalizar(c.get('clausula', ''))}" for c in datos.get("citas") or []}
    r["cita_correcta"] = bool(citadas & set(item["clausulas_correctas"]))
    r["abstencion_correcta"] = None
    if abstuvo:
        r.update(acierto=False, motivo="se abstuvo en una pregunta que sí tiene respuesta", abstencion_indebida=True)
        return r
    ok, motivo, costo = juzgar(cliente, item, datos)
    r.update(acierto=ok, motivo=motivo)
    r["costo_usd"] += costo
    return r


def porcentaje(valores: list) -> float | None:
    vals = [v for v in valores if v is not None]
    return round(100 * sum(vals) / len(vals), 1) if vals else None


def cargar_banco(rapido: bool, seguridad: bool) -> list[dict]:
    banco = json.loads((RAIZ / "data" / "banco_preguntas.json").read_text(encoding="utf-8"))
    if rapido:
        por_tipo: dict[str, list] = {}
        for item in banco:
            por_tipo.setdefault(item["tipo"], []).append(item)
        rng = random.Random(7)
        elegidas = []
        for items in por_tipo.values():
            elegidas += rng.sample(items, max(1, round(20 * len(items) / len(banco))))
        banco = elegidas[:20]
    archivo_seguridad = RAIZ / "data" / "banco_seguridad.json"
    if seguridad and archivo_seguridad.exists():
        banco += json.loads(archivo_seguridad.read_text(encoding="utf-8"))
    return banco


def enviar_tablero(fila: dict) -> str:
    url, token = os.environ.get("TABLERO_URL"), os.environ.get("TABLERO_TOKEN", "")
    pendientes = RAIZ / ".taller" / "pendientes.jsonl"
    if not url:
        return "sin TABLERO_URL: no se envió"
    cuerpo = json.dumps({"token": token, "tipo": "eval", **fila}, ensure_ascii=False).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=cuerpo, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=40) as resp:
            respuesta = json.loads(resp.read().decode("utf-8") or "{}")
        if respuesta.get("ok") is not True:
            raise RuntimeError(str(respuesta.get("error", "respuesta sin ok")))
        return "enviado al tablero"
    except Exception as e:  # red corporativa, proxy, etc.: se guarda para reenviar
        pendientes.parent.mkdir(exist_ok=True)
        with open(pendientes, "a", encoding="utf-8") as f:
            f.write(json.dumps({"token": token, "tipo": "eval", **fila}, ensure_ascii=False) + "\n")
        return f"no se pudo enviar ({type(e).__name__}: {e}); quedó en .taller/pendientes.jsonl"


def hay_credenciales() -> bool:
    """API key en .env, o un perfil de la CLI `ant` (ant auth login) que el SDK encuentra solo."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True
    try:
        from anthropic.lib.credentials import default_credentials

        return default_credentials() is not None
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Evalúa el asistente contra el banco de preguntas")
    ap.add_argument("--variante", default="base", help="nombre de la variante (la palanca de tu tarjeta)")
    ap.add_argument("--args", default="", help='argumentos extra para el asistente, por ejemplo "--k 3"')
    ap.add_argument("--rapido", action="store_true", help="solo 20 preguntas")
    ap.add_argument("--seguridad", action="store_true", help="suma las preguntas de seguridad del step 07")
    ap.add_argument("--concurrencia", type=int, default=3)
    ap.add_argument("--sin-envio", action="store_true", help="no manda el puntaje al tablero")
    argv = sys.argv[1:]
    if "--args" in argv and argv.index("--args") + 1 < len(argv):
        # `--args "--ejemplos"`: argparse would read a lone "--flag" value as a new option, so glue it.
        i = argv.index("--args")
        argv[i:i + 2] = [f"--args={argv[i + 1]}"]
    args = ap.parse_args(argv)

    if not hay_credenciales():
        sys.exit("Falta ANTHROPIC_API_KEY en el archivo .env de la raíz del repo.")
    banco = cargar_banco(args.rapido, args.seguridad)
    cmd = comando_asistente(args.args)
    cliente = anthropic.Anthropic(max_retries=4)
    consola.print(f"Evaluando {len(banco)} preguntas · variante [bold]{escape(args.variante)}[/bold] · {escape(' '.join(cmd[1:]))}")

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.concurrencia) as pool:
        resultados = list(pool.map(lambda it: evaluar_item(cmd, cliente, it), banco))
    minutos = (time.perf_counter() - t0) / 60

    metricas = {
        "acierto": porcentaje([r["acierto"] for r in resultados]),
        "cita_correcta": porcentaje([r["cita_correcta"] for r in resultados]),
        "abstencion_correcta": porcentaje([r["abstencion_correcta"] for r in resultados]),
    }
    validas = [v for v in metricas.values() if v is not None]
    puntaje = round(sum(validas) / len(validas), 1) if validas else 0.0
    costo = round(sum(r["costo_usd"] for r in resultados), 4)

    tabla = Table(title=f"Resultados por tipo de pregunta · variante {args.variante}")
    for col in ["Tipo", "Preguntas", "Acierto %", "Cita correcta %", "Abstención correcta %"]:
        tabla.add_column(col, justify="right" if col != "Tipo" else "left")
    for tipo in sorted({r["tipo"] for r in resultados}):
        grupo = [r for r in resultados if r["tipo"] == tipo]
        fmt = lambda v: "—" if v is None else f"{v:.0f}"  # noqa: E731
        tabla.add_row(tipo, str(len(grupo)), fmt(porcentaje([r["acierto"] for r in grupo])),
                      fmt(porcentaje([r["cita_correcta"] for r in grupo])),
                      fmt(porcentaje([r["abstencion_correcta"] for r in grupo])))
    consola.print(tabla)

    fallas = [r for r in resultados if r["acierto"] is False or r["abstencion_correcta"] is False]
    if fallas:
        consola.print("\n[bold]Preguntas que fallaron[/bold]")
        for r in fallas:
            consola.print(f"- {escape('[' + r['tipo'] + ']')} {escape(r['pregunta'])}\n    → {escape(str(r['motivo']))}")

    consola.print(
        f"\n[bold]Puntaje: {puntaje}[/bold] · acierto {metricas['acierto']} · cita correcta {metricas['cita_correcta']}"
        f" · abstención correcta {metricas['abstencion_correcta']} · costo USD {costo} · {minutos:.1f} min"
    )

    alias = (RAIZ / ".taller" / "alias").read_text(encoding="utf-8").strip() if (RAIZ / ".taller" / "alias").exists() else "sin-alias"
    fila = {"alias": alias, "variante": args.variante, "args": args.args, "preguntas": len(banco),
            "puntaje": puntaje, **metricas, "costo_usd": costo, "fecha": time.strftime("%Y-%m-%d %H:%M")}
    carpeta = RAIZ / "resultados"
    carpeta.mkdir(exist_ok=True)
    nombre = re.sub(r"[^a-zA-Z0-9_-]+", "-", f"{alias}-{args.variante}-{time.strftime('%H%M%S')}")
    (carpeta / f"{nombre}.json").write_text(
        json.dumps({**fila, "detalle": resultados}, ensure_ascii=False, indent=2), encoding="utf-8")
    consola.print(f"Detalle guardado en resultados/{nombre}.json")
    if not args.sin_envio:
        consola.print(enviar_tablero(fila))


if __name__ == "__main__":
    main()
