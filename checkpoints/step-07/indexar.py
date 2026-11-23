"""Indexa las pólizas en una base vectorial local (Chroma) — checkpoint step 07.

Lee el texto limpio de data/polizas/txt_limpio/ (sin texto invisible). Si no existe, corre la ingesta.

Uso:
    python mi-asistente/indexar.py                  # por cláusula (recomendado)
    python mi-asistente/indexar.py --chunking fijo  # cortes fijos de 800 caracteres, para comparar

Qué hace:
1. Parte cada póliza en pedazos (chunks): por artículo, o cada 800 caracteres.
2. Convierte cada pedazo en un vector de significado con multilingual-e5-small.
3. Guarda los vectores en .chroma/ (en la raíz del repo), uno por colección.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import sys  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chromadb  # noqa: E402
from chromadb.config import Settings  # noqa: E402


def buscar_raiz() -> Path:
    for carpeta in Path(__file__).resolve().parents:
        if (carpeta / "data" / "polizas").is_dir():
            return carpeta
    raise SystemExit("No encuentro la carpeta data/polizas.")


RAIZ = buscar_raiz()
DOCUMENTOS = ["hogar", "auto", "vida"]
MODELO_EMBEDDINGS = "intfloat/multilingual-e5-small"
TAMANO_FIJO = 800
ENCABEZADO = re.compile(r"^(Art\. \d+) — (.+)$", re.MULTILINE)


def leer(documento: str) -> str:
    archivo = RAIZ / "data" / "polizas" / "txt_limpio" / f"{documento}.txt"
    if not archivo.exists():
        from ingesta import main as ingerir

        ingerir()
    return archivo.read_text(encoding="utf-8")


def chunks_por_clausula(documento: str, texto: str) -> list[dict]:
    marcas = list(ENCABEZADO.finditer(texto))
    chunks = []
    for i, m in enumerate(marcas):
        fin = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        cuerpo = re.sub(r"\n?Capítulo [IVXLC]+ — .*$", "", texto[m.start():fin].strip(), flags=re.MULTILINE)
        chunks.append({"id": f"{documento}-{m.group(1)}", "texto": cuerpo.strip(),
                       "documento": documento, "clausulas": m.group(1)})
    return chunks


def chunks_fijos(documento: str, texto: str) -> list[dict]:
    chunks = []
    for n, inicio in enumerate(range(0, len(texto), TAMANO_FIJO)):
        pedazo = texto[inicio:inicio + TAMANO_FIJO]
        # Artículos que aparecen en el pedazo, o el último que empezó antes (el pedazo es parte de ese).
        previos = ENCABEZADO.findall(texto[:inicio + TAMANO_FIJO])
        dentro = [a for a, _ in ENCABEZADO.findall(pedazo)]
        arts = dentro or ([previos[-1][0]] if previos else [])
        chunks.append({"id": f"{documento}-fijo-{n}", "texto": pedazo, "documento": documento,
                       "clausulas": ", ".join(arts)})
    return chunks


def modelo_embeddings():
    from sentence_transformers import SentenceTransformer

    try:  # primero sin red: el modelo ya se descargó en el setup
        return SentenceTransformer(MODELO_EMBEDDINGS, local_files_only=True)
    except Exception:
        return SentenceTransformer(MODELO_EMBEDDINGS)


def coleccion(chunking: str, crear: bool = False):
    cliente = chromadb.PersistentClient(path=str(RAIZ / ".chroma"), settings=Settings(anonymized_telemetry=False))
    nombre = f"polizas-limpio-{chunking}"
    if crear:
        try:
            cliente.delete_collection(nombre)
        except Exception:
            pass
        return cliente.create_collection(nombre, embedding_function=None, metadata={"hnsw:space": "cosine"})
    return cliente.get_collection(nombre, embedding_function=None)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunking", choices=["clausula", "fijo"], default="clausula")
    args = parser.parse_args()

    partir = chunks_por_clausula if args.chunking == "clausula" else chunks_fijos
    chunks = [c for d in DOCUMENTOS for c in partir(d, leer(d))]
    print(f"{len(chunks)} pedazos ({args.chunking}). Calculando embeddings con {MODELO_EMBEDDINGS}...")
    vectores = modelo_embeddings().encode(
        [f"passage: {c['texto']}" for c in chunks], normalize_embeddings=True, show_progress_bar=False
    )
    col = coleccion(args.chunking, crear=True)
    col.add(
        ids=[c["id"] for c in chunks],
        embeddings=vectores.tolist(),
        documents=[c["texto"] for c in chunks],
        metadatas=[{"documento": c["documento"], "clausulas": c["clausulas"]} for c in chunks],
    )
    print(f"OK: colección polizas-limpio-{args.chunking} con {col.count()} pedazos en .chroma/")


if __name__ == "__main__":
    main()
