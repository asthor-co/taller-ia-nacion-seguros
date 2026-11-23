"""Verificacion local de cada hito del tablero.

Uso (solo verifica, no envia nada):
    python .claude/skills/marcar-avance/hitos.py spec
    python .claude/skills/marcar-avance/hitos.py --todos

Para verificar y enviar al tablero se usa marcar.py (mismo directorio).

Los hitos que prueban el asistente lo llaman por su contrato:
    python mi-asistente/asistente.py --json "pregunta"
Para probar otra implementacion, defini ASISTENTE_CMD
(por ejemplo: ASISTENTE_CMD="python checkpoints/step-04/asistente.py").
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

RAIZ = Path(__file__).resolve().parents[3]
TALLER = RAIZ / ".taller"
DOCUMENTOS = {"hogar", "auto", "vida"}
TIMEOUT_ASISTENTE = 180  # el contrato pide 90 s; con razonamiento alto y RAG en frio puede tardar mas
TIMEOUT_PYTEST = 1200
GUARDRAILS = {"siempre_cita": "siempre cita", "cita_existe": "la cita existe", "absten": "sabe abstenerse"}


@dataclass
class Resultado:
    ok: bool
    valor: bool | int | float | str | None
    detalle: str


def _json(ruta: Path):
    return json.loads(ruta.read_text(encoding="utf-8"))


def comando_asistente() -> list[str]:
    cmd = os.environ.get("ASISTENTE_CMD", "").strip()
    if cmd:
        partes = shlex.split(cmd, posix=os.name != "nt")
        return [p.strip('"').strip("'") for p in partes]
    return [sys.executable, str(RAIZ / "mi-asistente" / "asistente.py")]


def _entorno_hijo() -> dict[str, str]:
    return {**os.environ, "PYTHONIOENCODING": "utf-8", "ANONYMIZED_TELEMETRY": "False"}


_cache_respuestas: dict[str, tuple[dict | None, str]] = {}


def preguntar(pregunta: str) -> tuple[dict | None, str]:
    """Corre la CLI con --json. Devuelve (datos, error)."""
    if pregunta in _cache_respuestas:
        return _cache_respuestas[pregunta]
    cmd = comando_asistente()
    if not os.environ.get("ASISTENTE_CMD") and not Path(cmd[1]).exists():
        return None, "no existe mi-asistente/asistente.py"
    try:
        p = subprocess.run([*cmd, "--json", pregunta], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=TIMEOUT_ASISTENTE, env=_entorno_hijo())
    except subprocess.TimeoutExpired:
        resultado: tuple[dict | None, str] = (None, f"el asistente tardo mas de {TIMEOUT_ASISTENTE} s")
    except OSError as e:
        resultado = (None, f"no se pudo ejecutar el asistente ({e})")
    else:
        if p.returncode != 0:
            ultima = (p.stderr.strip().splitlines() or ["sin detalle"])[-1]
            resultado = (None, f"el asistente termino con error: {ultima[:200]}")
        else:
            try:
                datos = json.loads(p.stdout)
                resultado = (datos, "") if isinstance(datos, dict) else (None, "la salida --json no es un objeto")
            except json.JSONDecodeError:
                resultado = (None, "la salida con --json no es JSON valido (tiene que imprimir solo el JSON)")
    _cache_respuestas[pregunta] = resultado
    return resultado


def normalizar(clausula: str) -> str:
    m = re.search(r"(\d+)", clausula or "")
    return f"Art. {int(m.group(1))}" if m else (clausula or "").strip()


def claves_citas(datos: dict) -> set[str]:
    return {f"{(c.get('documento') or '').strip().lower()}#{normalizar(str(c.get('clausula', '')))}"
            for c in (datos.get("citas") or []) if isinstance(c, dict)}


def indice_clausulas() -> set[str]:
    return {f"{c['documento']}#{c['clausula']}" for c in _json(RAIZ / "data" / "polizas" / "clausulas.json")}


def ejemplos() -> list[dict]:
    return _json(RAIZ / "data" / "preguntas_ejemplo.json")


# ---------------------------------------------------------------- hitos


def entorno_listo() -> Resultado:
    marca = TALLER / "setup_ok"
    if marca.exists():
        return Resultado(True, True, "check_setup.py paso sin FALLAS")
    return Resultado(False, None, "corre python check_setup.py (sin --offline) hasta que no quede ninguna FALLA")


def step_01() -> Resultado:
    salida = TALLER / "step01_con_poliza.txt"
    if salida.exists() and salida.read_text(encoding="utf-8").strip():
        return Resultado(True, True, "hay salida de 02_con_poliza.py")
    return Resultado(False, None, "corre python steps/step-01/02_con_poliza.py")


def _plantilla() -> Path:
    propia = Path(__file__).resolve().parents[1] / "escribir-spec" / "plantilla.md"
    return propia if propia.exists() else RAIZ / "specs" / "plantilla-asistente.md"


def _secciones(texto: str) -> dict[str, str]:
    """Titulo normalizado de cada seccion '## ' -> contenido hasta la siguiente."""
    partes = re.split(r"^##\s+(.+?)\s*$", texto, flags=re.MULTILINE)
    secciones = {}
    for i in range(1, len(partes), 2):
        titulo = re.sub(r"^\d+[.)]?\s*", "", partes[i]).strip().lower()
        secciones[titulo] = partes[i + 1]
    return secciones


def _compacto(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


def spec() -> Resultado:
    archivo = RAIZ / "specs" / "asistente.md"
    if not archivo.exists():
        return Resultado(False, None, "no existe specs/asistente.md (usa el skill escribir-spec)")
    texto = archivo.read_text(encoding="utf-8")
    plantilla = _plantilla().read_text(encoding="utf-8")
    propias, esperadas = _secciones(texto), _secciones(plantilla)
    faltan = [t for t in esperadas if t not in propias]
    if faltan:
        return Resultado(False, None, "faltan secciones de la plantilla: " + ", ".join(faltan))
    contrato = next(t for t in esperadas if t.startswith("contrato"))
    if _compacto(propias[contrato]) != _compacto(esperadas[contrato]):
        return Resultado(False, None, "la seccion 'Contrato tecnico' cambio: copiala tal cual de la plantilla")
    marcadores = [linea.strip() for linea in plantilla.splitlines()
                  if re.search(r"<[^>\s][^>]*>", linea) and linea.strip() in {x.strip() for x in texto.splitlines()}]
    if marcadores:
        return Resultado(False, None, f"quedan {len(marcadores)} lineas sin completar, por ejemplo: {marcadores[0][:60]}")
    return Resultado(True, True, "specs/asistente.md completa y con el contrato intacto")


def plan_aprobado() -> Resultado:
    archivo = RAIZ / "specs" / "plan.md"
    if not archivo.exists():
        return Resultado(False, None, "no existe specs/plan.md (guarda ahi el plan que armo Claude Code)")
    m = re.search(r"^[\s*_>-]*Aprobado por[\s*_]*:[\s*_]*(.+?)[\s*_]*$", archivo.read_text(encoding="utf-8"),
                  flags=re.MULTILINE | re.IGNORECASE)
    if not m or not m.group(1).strip() or m.group(1).strip().startswith("<"):
        return Resultado(False, None, "falta la linea 'Aprobado por: <alias de tu pareja>' en specs/plan.md")
    return Resultado(True, True, f"plan aprobado por {m.group(1).strip()}")


def primera_cita() -> Resultado:
    indice = indice_clausulas()
    ultimo_error = "ninguna respuesta trajo una cita a una clausula existente"
    for ejemplo in ejemplos():
        datos, error = preguntar(ejemplo["pregunta"])
        if datos is None:
            return Resultado(False, None, error)
        existentes = claves_citas(datos) & indice
        if existentes:
            return Resultado(True, True, f"{ejemplo['id']} responde citando {sorted(existentes)[0].replace('#', ' ')}")
        if datos.get("citas"):
            ultimo_error = f"{ejemplo['id']} cita clausulas que no existen: {sorted(claves_citas(datos))}"
    return Resultado(False, None, ultimo_error)


def ejemplos_ok() -> Resultado:
    lista = ejemplos()
    fallan = []
    for ejemplo in lista:
        datos, error = preguntar(ejemplo["pregunta"])
        if datos is None:
            return Resultado(False, None, error)
        if not claves_citas(datos) & set(ejemplo["clausulas_correctas"]):
            fallan.append(ejemplo["id"])
    bien = len(lista) - len(fallan)
    if fallan:
        return Resultado(False, None, f"{bien}/{len(lista)} con la cita correcta; fallan {', '.join(fallan)} "
                                      "(revisa data/preguntas_ejemplo.json y corregi la spec)")
    return Resultado(True, True, f"{bien}/{len(lista)} preguntas de ejemplo con la cita correcta")


def _pytest(argumentos: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "pytest", *argumentos], cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout, env=_entorno_hijo())


def _guardrail(funcion: str) -> str | None:
    return next((clave for clave in GUARDRAILS if clave in funcion), None)


def guardrails() -> Resultado:
    carpeta = RAIZ / "mi-asistente" / "tests"
    if not carpeta.is_dir():
        return Resultado(False, None, "no existe mi-asistente/tests (pedile los guardrails a Claude Code)")
    rel = str(carpeta.relative_to(RAIZ))
    try:
        listado = _pytest([rel, "--collect-only", "-q", "-p", "no:cacheprovider"], timeout=120)
    except subprocess.TimeoutExpired:
        return Resultado(False, None, "pytest tardo demasiado en encontrar los tests")
    funciones = {re.sub(r"\[.*$", "", linea.split("::")[-1]).strip()
                 for linea in listado.stdout.splitlines() if "::" in linea}
    if not funciones:
        return Resultado(False, None, "pytest no encontro tests en mi-asistente/tests")
    conocidas = sorted(f for f in funciones if _guardrail(f))
    seleccion = ["-k", " or ".join(conocidas)] if conocidas else []

    with tempfile.TemporaryDirectory() as tmp:
        reporte = Path(tmp) / "guardrails.xml"
        try:
            _pytest([rel, "-q", "-p", "no:cacheprovider", f"--junitxml={reporte}", *seleccion], TIMEOUT_PYTEST)
        except subprocess.TimeoutExpired:
            return Resultado(False, None, f"los guardrails tardaron mas de {TIMEOUT_PYTEST // 60} minutos")
        if not reporte.exists():
            return Resultado(False, None, "pytest no genero el reporte (corre: pytest mi-asistente/tests -v)")
        casos = ET.parse(reporte).getroot().iter("testcase")
        estado: dict[str, bool] = {}
        for caso in casos:
            funcion = re.sub(r"\[.*$", "", caso.get("name", ""))
            if caso.find("skipped") is not None:
                continue
            paso = caso.find("failure") is None and caso.find("error") is None
            estado[funcion] = estado.get(funcion, True) and paso

    if conocidas:
        por_guardrail: dict[str, bool] = {}
        for funcion, paso in estado.items():
            clave = _guardrail(funcion)
            if clave:
                por_guardrail[clave] = por_guardrail.get(clave, True) and paso
        pasan = sum(por_guardrail.values())
        nombres = [GUARDRAILS[c] for c, paso in por_guardrail.items() if paso]
    else:
        pasan = min(3, sum(estado.values()))
        nombres = [f for f, paso in estado.items() if paso][:3]
    detalle = f"{pasan}/3 guardrails pasan" + (f" ({', '.join(nombres)})" if nombres else "")
    return Resultado(True, pasan, detalle)


def step_05() -> Resultado:
    candidatos = [RAIZ / ".chroma" / "chroma.sqlite3", *(RAIZ / "mi-asistente").rglob("chroma.sqlite3")]
    indices = [p for p in candidatos if p.exists()]
    if not indices:
        return Resultado(False, None, "no encuentro un indice de Chroma (corre python mi-asistente/indexar.py)")
    ejemplo = ejemplos()[0]
    datos, error = preguntar(ejemplo["pregunta"])
    if datos is None:
        return Resultado(False, None, error)
    citas = [c for c in datos.get("citas") or [] if isinstance(c, dict)]
    completas = [c for c in citas if (c.get("documento") or "").lower() in DOCUMENTOS
                 and re.search(r"\d+", str(c.get("clausula", "")))]
    if not completas:
        return Resultado(False, None, "la respuesta no trae citas con documento y clausula")
    c = completas[0]
    return Resultado(True, True, f"indice encontrado; la respuesta cita {c['documento']} {normalizar(str(c['clausula']))}")


def _resultados_eval(base: bool) -> list[tuple[Path, dict]]:
    carpeta = RAIZ / "resultados"
    hallados = []
    for archivo in sorted(carpeta.glob("*.json"), key=lambda p: p.stat().st_mtime) if carpeta.is_dir() else []:
        try:
            datos = _json(archivo)
        except (OSError, ValueError):
            continue
        variante = str(datos.get("variante", "base") or "base")
        if (variante == "base") == base:
            hallados.append((archivo, datos))
    return hallados


def eval_base() -> Resultado:
    hallados = _resultados_eval(base=True)
    if not hallados:
        return Resultado(False, None, "no hay resultados de la eval base (corre python steps/step-06/evaluar.py)")
    archivo, datos = hallados[-1]
    return Resultado(True, datos.get("puntaje", True), f"{archivo.name}: puntaje {datos.get('puntaje')}")


def eval_variante() -> Resultado:
    hallados = _resultados_eval(base=False)
    if not hallados:
        return Resultado(False, None, 'no hay resultados con variante (evaluar.py --variante "..." --args "...")')
    archivo, datos = hallados[-1]
    return Resultado(True, datos.get("puntaje", True),
                     f"{archivo.name}: variante {datos.get('variante')}, puntaje {datos.get('puntaje')}")


def step_07() -> Resultado:
    banco = RAIZ / "data" / "banco_seguridad.json"
    if not banco.exists():
        return Resultado(False, None, "este hito se habilita mas adelante en el taller")
    items = _json(banco)
    fallan = []
    for item in items:
        datos, error = preguntar(item["pregunta"])
        if datos is None:
            return Resultado(False, None, error)
        if datos.get("veredicto") != item["veredicto_esperado"]:
            fallan.append(item["id"])
    bien = len(items) - len(fallan)
    if fallan:
        return Resultado(False, None, f"{bien}/{len(items)} preguntas de data/banco_seguridad.json bien; fallan {', '.join(fallan)}")
    return Resultado(True, True, f"{bien}/{len(items)} preguntas de data/banco_seguridad.json bien")


HITOS: dict[str, Callable[[], Resultado]] = {
    "entorno_listo": entorno_listo,
    "step_01": step_01,
    "spec": spec,
    "plan_aprobado": plan_aprobado,
    "primera_cita": primera_cita,
    "ejemplos_ok": ejemplos_ok,
    "guardrails": guardrails,
    "step_05": step_05,
    "eval_base": eval_base,
    "eval_variante": eval_variante,
    "step_07": step_07,
}


def verificar(hito: str) -> Resultado:
    if hito not in HITOS:
        return Resultado(False, None, f"hito desconocido. Hitos: {', '.join(HITOS)}")
    try:
        return HITOS[hito]()
    except Exception as e:  # noqa: BLE001 - el participante tiene que ver un mensaje, no un traceback
        return Resultado(False, None, f"error al verificar ({type(e).__name__}: {str(e)[:150]})")


def main() -> int:
    try:
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    pedidos = list(HITOS) if "--todos" in sys.argv or len(sys.argv) < 2 else [a for a in sys.argv[1:] if a != "--todos"]
    sin_cumplir = 0
    for hito in pedidos:
        r = verificar(hito)
        sin_cumplir += not r.ok
        print(f"[{'OK' if r.ok else 'PENDIENTE'}]".ljust(12) + f"{hito}: {r.detalle}", flush=True)
    return 1 if sin_cumplir else 0


if __name__ == "__main__":
    sys.exit(main())
