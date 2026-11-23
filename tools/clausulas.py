"""Índice de cláusulas de las pólizas (lo usan los guardrails y las evals).

Uso:
    python tools/clausulas.py            # regenera data/polizas/clausulas.json

Desde Python:
    from tools.clausulas import cargar_indice, existe
    existe("hogar", "Art. 14")  -> True / False
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TXTS = RAIZ / "data" / "polizas" / "txt"
INDICE = RAIZ / "data" / "polizas" / "clausulas.json"
DOCUMENTOS = ["hogar", "auto", "vida"]

ENCABEZADO = re.compile(r"^(Art\. \d+) — (.+)$")
CAPITULO = re.compile(r"^Capítulo [IVXLC]+ — ")


def partir(documento: str, texto: str) -> list[dict]:
    clausulas: list[dict] = []
    actual: dict | None = None
    for linea in texto.splitlines():
        m = ENCABEZADO.match(linea.strip())
        if m:
            if actual:
                clausulas.append(actual)
            actual = {"documento": documento, "clausula": m.group(1), "titulo": m.group(2).strip(), "lineas": []}
        elif actual is not None and not CAPITULO.match(linea.strip()):
            actual["lineas"].append(linea)
    if actual:
        clausulas.append(actual)
    for c in clausulas:
        c["texto"] = re.sub(r"\s+", " ", " ".join(c.pop("lineas"))).strip()
    return clausulas


def construir() -> list[dict]:
    todas: list[dict] = []
    for doc in DOCUMENTOS:
        ruta = TXTS / f"{doc}.txt"
        if ruta.exists():
            todas.extend(partir(doc, ruta.read_text(encoding="utf-8")))
    return todas


def normalizar_id(clausula: str) -> str:
    m = re.search(r"(\d+)", clausula or "")
    return f"Art. {int(m.group(1))}" if m else (clausula or "").strip()


def cargar_indice() -> dict[tuple[str, str], dict]:
    datos = json.loads(INDICE.read_text(encoding="utf-8"))
    return {(c["documento"], c["clausula"]): c for c in datos}


def existe(documento: str, clausula: str) -> bool:
    return ((documento or "").strip().lower(), normalizar_id(clausula)) in cargar_indice()


def main() -> int:
    todas = construir()
    INDICE.write_text(json.dumps(todas, ensure_ascii=False, indent=2), encoding="utf-8")
    por_doc = {d: sum(1 for c in todas if c["documento"] == d) for d in DOCUMENTOS}
    print(f"OK {INDICE.relative_to(RAIZ)}: {por_doc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
