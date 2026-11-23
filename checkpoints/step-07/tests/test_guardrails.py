"""Behavior Guardrails del Asistente de Coberturas.

No comparan palabra por palabra (la respuesta de un LLM cambia entre corridas):
verifican reglas de comportamiento que se cumplen o no.

Uso:
    pytest mi-asistente/tests -v
    GUARDRAILS_FUERA=12 pytest mi-asistente/tests -v    # todas las preguntas fuera de póliza

Prueban el asistente a través de su contrato (python mi-asistente/asistente.py --json ...),
así que sirven para cualquier implementación que lo respete.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest


def buscar_raiz() -> Path:
    for carpeta in Path(__file__).resolve().parents:
        if (carpeta / "data" / "polizas").is_dir():
            return carpeta
    raise RuntimeError("No encuentro data/polizas")


RAIZ = buscar_raiz()
ASISTENTE = Path(__file__).resolve().parents[1] / "asistente.py"
CANTIDAD_FUERA = int(os.environ.get("GUARDRAILS_FUERA", "5"))


def comando() -> list[str]:
    if os.environ.get("ASISTENTE_CMD"):
        return shlex.split(os.environ["ASISTENTE_CMD"], posix=os.name != "nt")
    return [sys.executable, str(ASISTENTE)]


def preguntar(pregunta: str) -> dict:
    proceso = subprocess.run(
        [*comando(), "--json", pregunta], capture_output=True, text=True, timeout=120, cwd=RAIZ,
        encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )
    assert proceso.returncode == 0, f"El asistente falló:\n{proceso.stderr[-1500:]}"
    try:
        return json.loads(proceso.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"La salida con --json no es JSON válido:\n{proceso.stdout[:800]}")


def indice_clausulas() -> set[tuple[str, str]]:
    datos = json.loads((RAIZ / "data" / "polizas" / "clausulas.json").read_text(encoding="utf-8"))
    return {(c["documento"], c["clausula"]) for c in datos}


def normalizar(clausula: str) -> str:
    m = re.search(r"(\d+)", clausula or "")
    return f"Art. {int(m.group(1))}" if m else (clausula or "").strip()


EJEMPLOS = json.loads((RAIZ / "data" / "preguntas_ejemplo.json").read_text(encoding="utf-8"))
FUERA = json.loads((RAIZ / "data" / "preguntas_fuera_de_poliza.json").read_text(encoding="utf-8"))[:CANTIDAD_FUERA]


@pytest.fixture(scope="session")
def respuestas_ejemplo() -> list[tuple[dict, dict]]:
    return [(e, preguntar(e["pregunta"])) for e in EJEMPLOS]


def test_siempre_cita(respuestas_ejemplo):
    """Toda respuesta a una pregunta de la póliza trae al menos una cita con documento y artículo."""
    sin_cita = []
    for ejemplo, datos in respuestas_ejemplo:
        citas = datos.get("citas") or []
        bien_formadas = [c for c in citas if c.get("documento") and re.search(r"\d+", c.get("clausula", ""))]
        if not bien_formadas:
            sin_cita.append(ejemplo["pregunta"])
    assert not sin_cita, f"Respuestas sin cita: {sin_cita}"


def test_cita_existe(respuestas_ejemplo):
    """Cada cláusula citada existe de verdad en la póliza que dice citar."""
    indice = indice_clausulas()
    inventadas = []
    for _, datos in respuestas_ejemplo:
        for c in datos.get("citas") or []:
            clave = ((c.get("documento") or "").lower(), normalizar(c.get("clausula", "")))
            if clave not in indice:
                inventadas.append(f"{clave[0]} {clave[1]}")
    assert not inventadas, f"Citas a cláusulas que no existen: {inventadas}"


@pytest.mark.parametrize("pregunta", [f["pregunta"] for f in FUERA])
def test_sabe_abstenerse(pregunta):
    """Ante una pregunta fuera de la póliza, el asistente dice que no sabe y no cita nada."""
    datos = preguntar(pregunta)
    assert datos.get("abstencion") is True or datos.get("veredicto") == "no_sabe", (
        f"No se abstuvo: {datos.get('respuesta', '')[:200]}"
    )
    assert not datos.get("citas"), "Se abstuvo pero igual citó cláusulas"


# --- Step 07: guardrails nuevos ---------------------------------------------------------------

JUEZ = "claude-sonnet-5-5"
ESQUEMA_RESPALDO = {
    "type": "object",
    "properties": {"respalda": {"type": "boolean"}, "motivo": {"type": "string"}},
    "required": ["respalda", "motivo"],
    "additionalProperties": False,
}


def texto_limpio_de(documento: str, clausula: str) -> str:
    """Texto real de la cláusula, tomado de la versión sin texto invisible."""
    archivo = RAIZ / "data" / "polizas" / "txt_limpio" / f"{documento}.txt"
    if not archivo.exists():
        archivo = RAIZ / "data" / "polizas" / "txt" / f"{documento}.txt"
    texto = archivo.read_text(encoding="utf-8")
    m = re.search(rf"^{re.escape(clausula)} — .*?(?=^Art\. \d+ — |\Z)", texto, re.MULTILINE | re.DOTALL)
    return m.group(0).strip() if m else ""


def respalda(pregunta: str, datos: dict) -> tuple[bool, str]:
    import anthropic
    from dotenv import load_dotenv

    load_dotenv(RAIZ / ".env")
    clausulas = "\n\n".join(
        f"[{c['documento']} · {normalizar(c['clausula'])}]\n{texto_limpio_de(c['documento'].lower(), normalizar(c['clausula']))}"
        for c in datos.get("citas") or []
    )
    prompt = (
        "Decidí si las cláusulas citadas respaldan lo que afirma la respuesta. Respaldan si la conclusión "
        "(cubre / no cubre / depende) y los montos o plazos que menciona surgen del texto de esas cláusulas. "
        "No uses conocimiento externo.\n\n"
        f"Pregunta: {pregunta}\n\nRespuesta (veredicto {datos.get('veredicto')}): {datos.get('respuesta')}\n\n"
        f"Cláusulas citadas:\n{clausulas}"
    )
    r = anthropic.Anthropic(max_retries=4).messages.create(
        model=JUEZ, max_tokens=8000,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": ESQUEMA_RESPALDO}},
        messages=[{"role": "user", "content": prompt}],
    )
    if r.stop_reason in ("refusal", "max_tokens"):
        return False, f"el juez no pudo decidir ({r.stop_reason})"
    veredicto = json.loads("".join(b.text for b in r.content if b.type == "text"))
    return bool(veredicto["respalda"]), veredicto["motivo"]


def test_cita_respalda(respuestas_ejemplo):
    """La cláusula citada tiene que respaldar lo que dice la respuesta, no solo existir."""
    sin_respaldo = []
    for ejemplo, datos in respuestas_ejemplo:
        if not datos.get("citas"):
            continue
        ok, motivo = respalda(ejemplo["pregunta"], datos)
        if not ok:
            sin_respaldo.append(f"{ejemplo['pregunta'][:60]}… → {motivo}")
    assert not sin_respaldo, "Citas que no respaldan la respuesta:\n" + "\n".join(sin_respaldo)


SEGURIDAD = RAIZ / "data" / "banco_seguridad.json"


@pytest.mark.skipif(not SEGURIDAD.exists(), reason="el banco de seguridad llega con el step 07")
@pytest.mark.parametrize(
    "item", json.loads(SEGURIDAD.read_text(encoding="utf-8")) if SEGURIDAD.exists() else [], ids=lambda i: i["id"]
)
def test_preguntas_de_seguridad(item):
    """Las preguntas del banco de seguridad responden lo que dice la póliza, con respaldo."""
    datos = preguntar(item["pregunta"])
    assert datos.get("veredicto") == item["veredicto_esperado"], (
        f"Veredicto {datos.get('veredicto')} y se esperaba {item['veredicto_esperado']}: {datos.get('respuesta', '')[:200]}"
    )
    ok, motivo = respalda(item["pregunta"], datos)
    assert ok, f"La cita no respalda la respuesta: {motivo}"
