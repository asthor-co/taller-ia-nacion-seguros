"""Convierte las pólizas en PDF a texto plano.

Uso:
    python tools/pdf_a_texto.py                  # todas las pólizas de data/polizas/pdf
    python tools/pdf_a_texto.py data/polizas/pdf/hogar.pdf

Qué hace:
- Extrae el texto de cada página con pdfplumber.
- Elimina el aviso del pie de página ("Material de entrenamiento elaborado por Asthor...")
  para que no ensucie el contexto del modelo.
- Deja cada encabezado "Art. N — Título" en su propia línea.
- Además guarda hogar_con_footer.txt (con el aviso) para la demo del step 01.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pdfplumber

RAIZ = Path(__file__).resolve().parents[1]
PDFS = RAIZ / "data" / "polizas" / "pdf"
TXTS = RAIZ / "data" / "polizas" / "txt"

AVISO = (
    "Material de entrenamiento elaborado por Asthor. Contenido ficticio, "
    "no constituye una póliza vigente de Nación Seguros."
)
# El aviso puede venir partido en varias líneas: se busca palabra por palabra.
# Al final de la línea viene el número de página, que también se descarta.
PATRON_AVISO = re.compile(r"\s+".join(re.escape(p) for p in AVISO.split()) + r"(?:[ \t]+\d{1,3})?")
ENCABEZADO = re.compile(r"\s*(Art\. \d+ — )")


def extraer_paginas(pdf_path: Path) -> list[str]:
    with pdfplumber.open(pdf_path) as pdf:
        return [pagina.extract_text() or "" for pagina in pdf.pages]


def limpiar(texto: str, quitar_aviso: bool = True) -> str:
    if quitar_aviso:
        texto = PATRON_AVISO.sub("", texto)
    texto = ENCABEZADO.sub(r"\n\n\1", texto)
    lineas = [l.rstrip() for l in texto.splitlines()]
    texto = "\n".join(lineas)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip() + "\n"


def convertir(pdf_path: Path) -> Path:
    paginas = extraer_paginas(pdf_path)
    TXTS.mkdir(parents=True, exist_ok=True)
    destino = TXTS / f"{pdf_path.stem}.txt"
    destino.write_text(limpiar("\n".join(paginas)), encoding="utf-8")
    if pdf_path.stem == "hogar":
        con_aviso = TXTS / "hogar_con_footer.txt"
        con_aviso.write_text(limpiar("\n".join(paginas), quitar_aviso=False), encoding="utf-8")
    return destino


def main() -> int:
    archivos = [Path(a) for a in sys.argv[1:]] or sorted(PDFS.glob("*.pdf"))
    if not archivos:
        print(f"No encontré PDFs en {PDFS}")
        return 1
    for pdf in archivos:
        destino = convertir(pdf)
        print(f"OK {pdf.name} -> {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
