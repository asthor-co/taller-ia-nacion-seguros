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
