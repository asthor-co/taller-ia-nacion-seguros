"""Salta a un checkpoint: copia una versión que funciona en mi-asistente/.

Uso:
    python tools/saltar.py step-03
    python tools/saltar.py --lista

Antes de copiar, mueve tu trabajo a mi-asistente.backup-<hora>/ para que no pierdas nada.
Para step-02 copia la spec de ejemplo en specs/asistente.md (si ya tenés una, la respalda).
"""

from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CHECKPOINTS = RAIZ / "checkpoints"
DESTINO = RAIZ / "mi-asistente"
IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")


def disponibles() -> list[str]:
    return sorted(p.name for p in CHECKPOINTS.iterdir() if p.is_dir())


def nombre_libre(base: Path, sufijo: str = "") -> Path:
    """base.backup-HHMMSS[-n]<sufijo>, sin pisar nada existente."""
    hora = time.strftime("%H%M%S")
    candidato = base.with_name(f"{base.stem}.backup-{hora}{sufijo}")
    n = 2
    while candidato.exists():
        candidato = base.with_name(f"{base.stem}.backup-{hora}-{n}{sufijo}")
        n += 1
    return candidato


def respaldar(ruta: Path) -> Path | None:
    if not ruta.exists():
        return None
    copia = nombre_libre(ruta, ruta.suffix)
    shutil.move(str(ruta), str(copia))
    return copia


def saltar(nombre: str) -> None:
    origen = CHECKPOINTS / nombre
    if not origen.is_dir():
        sys.exit(f"No existe el checkpoint {nombre}. Disponibles: {', '.join(disponibles())}")

    if nombre == "step-02":
        spec = RAIZ / "specs" / "asistente.md"
        copia = respaldar(spec)
        shutil.copy2(origen / "specs" / "asistente.md", spec)
        print(f"Listo: specs/asistente.md es ahora la spec de ejemplo." + (f" Tu versión quedó en {copia.name}." if copia else ""))
        return

    contenido = [p for p in DESTINO.iterdir() if p.name != "README.md"] if DESTINO.exists() else []
    copia = None
    if contenido:
        copia = nombre_libre(DESTINO)
        copia.mkdir()
        for p in contenido:
            shutil.move(str(p), str(copia / p.name))
    DESTINO.mkdir(exist_ok=True)
    for p in origen.iterdir():
        if p.is_dir():
            shutil.copytree(p, DESTINO / p.name, ignore=IGNORAR, dirs_exist_ok=True)
        else:
            shutil.copy2(p, DESTINO / p.name)
    print(f"Listo: mi-asistente/ tiene ahora el checkpoint {nombre}.")
    if copia:
        print(f"Tu trabajo anterior quedó en {copia.name}/")
    if (DESTINO / "indexar.py").exists():
        print("Este checkpoint usa la base vectorial: corré una vez  python mi-asistente/indexar.py")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__)
        sys.exit(0 if len(sys.argv) == 2 else 1)
    if sys.argv[1] == "--lista":
        print("\n".join(disponibles()))
        return
    saltar(sys.argv[1])


if __name__ == "__main__":
    main()
