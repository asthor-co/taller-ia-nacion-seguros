"""Ingesta segura de las pólizas — checkpoint step 07.

Uso:
    python mi-asistente/ingesta.py

Convierte los PDF a texto como tools/pdf_a_texto.py, pero antes descarta el texto que una
persona no puede ver: letra blanca o de menos de 4 puntos. Ese texto igual llega al modelo
si no se filtra, y puede traer instrucciones. Escribe data/polizas/txt_limpio/*.txt e informa
cuántos caracteres invisibles descartó en cada documento.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pdfplumber


def buscar_raiz() -> Path:
    for carpeta in Path(__file__).resolve().parents:
        if (carpeta / "data" / "polizas").is_dir():
            return carpeta
    raise SystemExit("No encuentro la carpeta data/polizas.")


RAIZ = buscar_raiz()
sys.path.insert(0, str(RAIZ))
from tools.pdf_a_texto import limpiar  # noqa: E402

DOCUMENTOS = ["hogar", "auto", "vida"]
TAMANO_MINIMO = 4.0


def es_blanco(color) -> bool:
    if color is None:
        return False
    valores = color if isinstance(color, (list, tuple)) else (color,)
    if len(valores) == 4:  # CMYK: blanco es (0, 0, 0, 0)
        return all(float(v) <= 0.02 for v in valores)
    return all(float(v) >= 0.98 for v in valores)  # gris o RGB


def es_invisible(obj: dict) -> bool:
    return obj.get("object_type") == "char" and (
        es_blanco(obj.get("non_stroking_color")) or float(obj.get("size", 10)) < TAMANO_MINIMO
    )


def convertir(documento: str) -> tuple[Path, int]:
    pdf_path = RAIZ / "data" / "polizas" / "pdf" / f"{documento}.pdf"
    paginas, descartados = [], 0
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            descartados += sum(1 for c in pagina.chars if es_invisible(c))
            visible = pagina.filter(lambda obj: not es_invisible(obj))
            paginas.append(visible.extract_text() or "")
    destino = RAIZ / "data" / "polizas" / "txt_limpio" / f"{documento}.txt"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(limpiar("\n".join(paginas)), encoding="utf-8")
    return destino, descartados


def main() -> None:
    for documento in DOCUMENTOS:
        destino, descartados = convertir(documento)
        aviso = f"  <-- se descartaron {descartados} caracteres invisibles" if descartados else ""
        print(f"OK {documento}: {destino.relative_to(RAIZ)}{aviso}")


if __name__ == "__main__":
    main()
