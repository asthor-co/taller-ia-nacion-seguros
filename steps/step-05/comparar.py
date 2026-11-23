"""Step 05 — Compara el asistente del día 1 (póliza entera) contra el de RAG.

Uso:
    python steps/step-05/comparar.py
    python steps/step-05/comparar.py --preguntas 8

Por defecto compara:
    día 1: python checkpoints/step-04/asistente.py   (póliza completa en el contexto)
    RAG:   python mi-asistente/asistente.py          (tu versión con base vectorial)
Para cambiarlos: ASISTENTE_V2_CMD y ASISTENTE_V3_CMD.

Mide, sobre las mismas preguntas del banco: tokens de entrada, costo y % de citas correctas.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from rich.console import Console
from rich.table import Table

RAIZ = Path(__file__).resolve().parents[2]


def comando(variable: str, por_defecto: Path) -> list[str]:
    return shlex.split(os.environ[variable], posix=os.name != "nt") if os.environ.get(variable) else [sys.executable, str(por_defecto)]


def normalizar(clausula: str) -> str:
    m = re.search(r"(\d+)", clausula or "")
    return f"Art. {int(m.group(1))}" if m else ""


def correr(cmd: list[str], item: dict) -> dict:
    try:
        p = subprocess.run([*cmd, "--json", item["pregunta"]], capture_output=True, text=True, timeout=240,
                           cwd=RAIZ, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    try:
        datos = json.loads(p.stdout)
        if not isinstance(datos, dict):
            raise json.JSONDecodeError("no es un objeto", p.stdout, 0)
    except json.JSONDecodeError:
        return {"error": (p.stderr or p.stdout)[-200:]}
    citadas = {f"{(c.get('documento') or '').lower()}#{normalizar(c.get('clausula', ''))}" for c in datos.get("citas") or []}
    uso = datos.get("uso") or {}
    return {
        "tokens": uso.get("tokens_entrada", 0),
        "costo": uso.get("costo_usd", 0.0),
        "cita_ok": bool(citadas & set(item["clausulas_correctas"])),
    }


def resumen(filas: list[dict]) -> dict:
    validas = [f for f in filas if "error" not in f]
    n = len(validas) or 1
    return {
        "tokens": sum(f["tokens"] for f in validas) / n,
        "costo": sum(f["costo"] for f in validas) / n,
        "citas": 100 * sum(f["cita_ok"] for f in validas) / n,
        "errores": len(filas) - len(validas),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preguntas", type=int, default=15)
    args = ap.parse_args()

    banco = [q for q in json.loads((RAIZ / "data" / "banco_preguntas.json").read_text(encoding="utf-8"))
             if not q["debe_abstenerse"]]
    paso = max(1, len(banco) // args.preguntas)
    muestra = banco[::paso][: args.preguntas]

    v2 = comando("ASISTENTE_V2_CMD", RAIZ / "checkpoints" / "step-04" / "asistente.py")
    v3 = comando("ASISTENTE_V3_CMD", RAIZ / "mi-asistente" / "asistente.py")
    consola = Console()
    consola.print(f"Comparando {len(muestra)} preguntas del banco…")
    with ThreadPoolExecutor(max_workers=3) as pool:
        r2 = list(pool.map(lambda q: correr(v2, q), muestra))
        r3 = list(pool.map(lambda q: correr(v3, q), muestra))
    a, b = resumen(r2), resumen(r3)

    tabla = Table(title="Día 1 (póliza entera) vs. RAG (solo cláusulas relevantes)")
    for col in ["", "Día 1", "RAG", "Cambio"]:
        tabla.add_column(col, justify="right" if col else "left")
    cambio = lambda x, y: f"{(y - x) / x * 100:+.0f} %" if x else "—"  # noqa: E731
    tabla.add_row("Tokens de entrada por pregunta", f"{a['tokens']:,.0f}".replace(",", "."), f"{b['tokens']:,.0f}".replace(",", "."), cambio(a["tokens"], b["tokens"]))
    tabla.add_row("Costo por pregunta (USD)", f"{a['costo']:.4f}", f"{b['costo']:.4f}", cambio(a["costo"], b["costo"]))
    tabla.add_row("Citas correctas", f"{a['citas']:.0f} %", f"{b['citas']:.0f} %", f"{b['citas'] - a['citas']:+.0f} puntos")
    consola.print(tabla)
    if a["errores"] or b["errores"]:
        consola.print(f"Errores: día 1 {a['errores']}, RAG {b['errores']} (revisá que corra con --json)")
    salida = RAIZ / ".taller" / "comparacion_step05.json"
    salida.parent.mkdir(exist_ok=True)
    salida.write_text(json.dumps({"dia1": a, "rag": b, "preguntas": len(muestra)}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
