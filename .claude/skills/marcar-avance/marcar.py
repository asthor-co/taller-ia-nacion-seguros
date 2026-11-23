"""Verifica un hito en tu maquina y lo marca en el tablero del taller.

Uso (desde la raiz del repo, con el entorno virtual activado):
    python .claude/skills/marcar-avance/marcar.py spec
    python .claude/skills/marcar-avance/marcar.py --todos            # verifica y envia todos los que falten
    python .claude/skills/marcar-avance/marcar.py --todos --forzar   # vuelve a verificar tambien los ya enviados
    python .claude/skills/marcar-avance/marcar.py --reenviar         # solo reenvia lo que quedo pendiente
    python .claude/skills/marcar-avance/marcar.py --alias mi-alias   # guarda tu alias en .taller/alias

Configuracion (archivo .env de la raiz): TABLERO_URL y TABLERO_TOKEN, los proyecta el instructor.
Si no estan o no hay conexion, el envio queda en .taller/pendientes.jsonl y se reenvia la proxima vez.

Protocolo: POST application/json
    {"token": ..., "tipo": "hito", "alias": ..., "hito": ..., "valor": true | numero | texto, "fecha": "YYYY-MM-DD HH:MM"}
Respuesta esperada: {"ok": true}
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hitos import HITOS, RAIZ, TALLER, verificar  # noqa: E402

PENDIENTES = TALLER / "pendientes.jsonl"
ENVIADOS = TALLER / "enviados.json"
TIMEOUT_ENVIO = 15


def cargar_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(RAIZ / ".env")


def leer_alias() -> str:
    archivo = TALLER / "alias"
    return archivo.read_text(encoding="utf-8").strip() if archivo.exists() else ""


def guardar_alias(alias: str) -> str:
    alias = re.sub(r"\s+", "-", alias.strip())[:40]
    TALLER.mkdir(exist_ok=True)
    (TALLER / "alias").write_text(alias + "\n", encoding="utf-8")
    return alias


def sin_token(cuerpo: dict) -> str:
    return json.dumps({**cuerpo, "token": "***" if cuerpo.get("token") else ""}, ensure_ascii=False)


def enviar(cuerpo: dict) -> tuple[bool, str]:
    """POST al tablero. Devuelve (ok, motivo)."""
    url = os.environ.get("TABLERO_URL", "").strip()
    if not url:
        return False, "sin TABLERO_URL (modo offline)"
    datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
    pedido = urllib.request.Request(url, data=datos, method="POST",
                                    headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(pedido, timeout=TIMEOUT_ENVIO) as r:
            texto = r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return False, f"el tablero respondio HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return False, f"sin conexion con el tablero ({type(e).__name__})"
    try:
        respuesta = json.loads(texto)
    except ValueError:
        return False, "la respuesta del tablero no es JSON (revisa TABLERO_URL)"
    if isinstance(respuesta, dict) and respuesta.get("ok") is True:
        return True, "ok"
    motivo = respuesta.get("error") if isinstance(respuesta, dict) else None
    return False, f"el tablero rechazo el envio ({motivo or 'sin detalle'})"


def encolar(cuerpo: dict) -> None:
    TALLER.mkdir(exist_ok=True)
    with open(PENDIENTES, "a", encoding="utf-8") as f:
        f.write(json.dumps(cuerpo, ensure_ascii=False) + "\n")


def reenviar_pendientes() -> None:
    if not PENDIENTES.exists():
        return
    lineas = [x for x in PENDIENTES.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not lineas:
        return
    if not os.environ.get("TABLERO_URL", "").strip():
        print(f"Hay {len(lineas)} envios pendientes en .taller/pendientes.jsonl (se mandan cuando haya TABLERO_URL).")
        return
    token = os.environ.get("TABLERO_TOKEN", "")
    quedan, enviados = [], 0
    for linea in lineas:
        try:
            cuerpo = json.loads(linea)
        except ValueError:
            continue
        # El token es el de la sala: si se corrigio en .env, se reenvia con el actual.
        cuerpo["token"] = token or cuerpo.get("token", "")
        ok, motivo = enviar(cuerpo)
        if ok:
            enviados += 1
            print(f"Reenviado: {sin_token(cuerpo)}")
        else:
            quedan.append(json.dumps(cuerpo, ensure_ascii=False))
            if len(quedan) == 1:
                print(f"No se pudo reenviar: {motivo}")
    PENDIENTES.write_text("".join(x + "\n" for x in quedan), encoding="utf-8")
    if enviados or quedan:
        print(f"Pendientes: {enviados} reenviados, {len(quedan)} siguen en cola.")


def leer_enviados() -> dict:
    try:
        return json.loads(ENVIADOS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def registrar_enviado(hito: str, valor) -> None:
    datos = leer_enviados()
    datos[hito] = {"valor": valor, "fecha": time.strftime("%Y-%m-%d %H:%M")}
    TALLER.mkdir(exist_ok=True)
    ENVIADOS.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def ya_completo(hito: str, enviados: dict) -> bool:
    if hito not in enviados:
        return False
    return hito != "guardrails" or (enviados[hito].get("valor") or 0) >= 3


def marcar(hito: str, alias: str) -> bool:
    print(f"\n== {hito}")
    r = verificar(hito)
    if not r.ok:
        print(f"[PENDIENTE] {r.detalle}")
        return False
    print(f"[OK]        {r.detalle}")
    cuerpo = {
        "token": os.environ.get("TABLERO_TOKEN", ""),
        "tipo": "hito",
        "alias": alias,
        "hito": hito,
        "valor": r.valor,
        "fecha": time.strftime("%Y-%m-%d %H:%M"),
    }
    ok, motivo = enviar(cuerpo)
    if ok:
        print(f"Enviado al tablero: {sin_token(cuerpo)}")
    else:
        encolar(cuerpo)
        print(f"No se envio ({motivo}). Quedo en .taller/pendientes.jsonl: {sin_token(cuerpo)}")
    registrar_enviado(hito, r.valor)
    return True


def main() -> int:
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="Marca hitos del taller en el tablero")
    ap.add_argument("hitos", nargs="*", help=f"uno o mas de: {', '.join(HITOS)}")
    ap.add_argument("--todos", action="store_true", help="verifica y envia todos los hitos que falten")
    ap.add_argument("--forzar", action="store_true", help="con --todos, vuelve a verificar los ya enviados")
    ap.add_argument("--reenviar", action="store_true", help="solo reenvia los pendientes")
    ap.add_argument("--alias", help="guarda tu alias en .taller/alias")
    args = ap.parse_args()

    cargar_env()
    if args.alias:
        print(f"Alias guardado: {guardar_alias(args.alias)}")
    alias = leer_alias()
    if not alias:
        print("Falta tu alias. Guardalo con: python .claude/skills/marcar-avance/marcar.py --alias tu-alias")
        return 1

    reenviar_pendientes()
    if args.reenviar or (args.alias and not args.hitos and not args.todos):
        return 0

    desconocidos = [h for h in args.hitos if h not in HITOS]
    if desconocidos:
        print(f"Hito desconocido: {', '.join(desconocidos)}. Hitos: {', '.join(HITOS)}")
        return 1
    if args.todos:
        enviados = {} if args.forzar else leer_enviados()
        pedidos = []
        for hito in HITOS:
            if ya_completo(hito, enviados):
                print(f"(ya marcado: {hito}; usa --forzar para volver a verificarlo)")
            else:
                pedidos.append(hito)
    elif args.hitos:
        pedidos = args.hitos
    else:
        ap.print_help()
        return 1

    marcados = [h for h in pedidos if marcar(h, alias)]
    print(f"\nResumen: {len(marcados)} de {len(pedidos)} hitos verificados"
          + (f" ({', '.join(marcados)})" if marcados else ""))
    return 0 if len(marcados) == len(pedidos) else 1


if __name__ == "__main__":
    sys.exit(main())
