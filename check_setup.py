"""Chequeo del entorno del taller.

Uso (desde la raiz del repo, con el entorno virtual activado):
    python check_setup.py             # chequeo completo (hace una llamada minima a la API)
    python check_setup.py --offline   # sin llamadas a la API ni a internet (para CI)

Imprime OK / PENDIENTE / FALLA por item, con el arreglo sugerido.
Termina con codigo 0 solo si no hay ninguna FALLA. Si el chequeo completo pasa,
deja la marca .taller/setup_ok (la usa el hito entorno_listo de marcar-avance).

La salida es texto plano (sin colores ni emojis) para que se lea bien en cmd de Windows.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
import io
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
MODELO_EMBEDDINGS = "intfloat/multilingual-e5-small"
MODELO_PRUEBA = "claude-haiku-5-5"
POLIZAS = ["hogar", "auto", "vida"]
MODULOS = {
    "anthropic": "anthropic",
    "python-dotenv": "dotenv",
    "pdfplumber": "pdfplumber",
    "chromadb": "chromadb",
    "sentence-transformers": "sentence_transformers",
    "pytest": "pytest",
    "rich": "rich",
}
COMANDO_DESCARGA = (
    'python -c "from sentence_transformers import SentenceTransformer; '
    "SentenceTransformer('intfloat/multilingual-e5-small')\""
)

# Chroma intenta mandar telemetria a internet si no se apaga; detras de un proxy eso tira errores.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
# Este chequeo nunca descarga nada: solo mira lo que ya esta en la cache.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

OK, PENDIENTE, FALLA = "OK", "PENDIENTE", "FALLA"
resultados: list[tuple[str, str, str, str]] = []


def registrar(estado: str, item: str, detalle: str = "", arreglo: str = "") -> None:
    resultados.append((estado, item, detalle, arreglo))
    print(f"[{estado}]".ljust(12) + f"{item}" + (f": {detalle}" if detalle else ""), flush=True)
    if arreglo and estado != OK:
        for linea in arreglo.splitlines():
            print(" " * 12 + f"-> {linea}", flush=True)


def silencio():
    """Oculta avisos y barras de progreso de torch/transformers (no se leen bien en cmd)."""
    return contextlib.redirect_stderr(io.StringIO())


def es_venv() -> bool:
    return sys.prefix != sys.base_prefix


def chequear_python() -> None:
    v = sys.version_info
    texto = f"{v.major}.{v.minor}.{v.micro} ({sys.executable})"
    if v < (3, 11):
        registrar(FALLA, "Python", texto, "Hace falta Python 3.11 o superior (recomendado 3.12). Ver docs/setup.md.")
    elif v >= (3, 14):
        registrar(PENDIENTE, "Python", texto, "Probado con 3.11 a 3.13. Si algo falla al instalar, usa Python 3.12.")
    elif not es_venv():
        registrar(PENDIENTE, "Python", texto + " fuera del entorno virtual",
                  "Activa el entorno: Windows .venv\\Scripts\\activate  |  macOS source .venv/bin/activate")
    else:
        registrar(OK, "Python", texto)


def versiones_fijadas() -> dict[str, str]:
    fijadas = {}
    archivo = RAIZ / "requirements.txt"
    if archivo.exists():
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            linea = linea.split("#")[0].strip()
            if "==" in linea:
                nombre, version = linea.split("==", 1)
                fijadas[nombre.strip().lower()] = version.strip()
    return fijadas


def chequear_librerias() -> bool:
    faltan, distintas = [], []
    fijadas = versiones_fijadas()
    for paquete, modulo in MODULOS.items():
        try:
            with silencio():
                importlib.import_module(modulo)
        except Exception as e:  # noqa: BLE001 - cualquier error de import es una falla de instalacion
            faltan.append(f"{paquete} ({type(e).__name__})")
            continue
        try:
            instalada = importlib.metadata.version(paquete)
        except importlib.metadata.PackageNotFoundError:
            instalada = "?"
        esperada = fijadas.get(paquete)
        if esperada and instalada != esperada:
            distintas.append(f"{paquete} {instalada} (se espera {esperada})")
    if faltan:
        registrar(FALLA, "Librerias", "no se pueden importar: " + ", ".join(faltan),
                  "Con el entorno activado: python -m pip install -r requirements.txt")
        return False
    if distintas:
        registrar(PENDIENTE, "Librerias", "versiones distintas: " + ", ".join(distintas),
                  "python -m pip install -r requirements.txt")
        return True
    registrar(OK, "Librerias", f"{len(MODULOS)} paquetes con las versiones fijadas")
    return True


def chequear_git() -> None:
    if not shutil.which("git"):
        registrar(FALLA, "Git", "no esta instalado o no esta en el PATH",
                  "Windows: winget install Git.Git  |  macOS: xcode-select --install")
        return
    p = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=RAIZ, capture_output=True, text=True)
    if p.returncode != 0:
        registrar(PENDIENTE, "Git", "esta carpeta no es un repo git",
                  "Clona el repo del taller con git clone (no lo descargues como zip).")
        return
    registrar(OK, "Git", "repo del taller")


def chequear_claude_code() -> None:
    if shutil.which("claude"):
        registrar(OK, "Claude Code", "comando claude disponible")
    else:
        registrar(PENDIENTE, "Claude Code", "no encuentro el comando claude en el PATH",
                  "Ver docs/setup.md, seccion Claude Code (instalador nativo).")


def chequear_env(offline: bool) -> None:
    archivo = RAIZ / ".env"
    ignorado = None
    if shutil.which("git"):
        p = subprocess.run(["git", "check-ignore", "-q", ".env"], cwd=RAIZ, capture_output=True, text=True)
        ignorado = p.returncode == 0
    if ignorado is False:
        registrar(FALLA, "Archivo .env", "git NO lo ignora: la key podria subirse al repo",
                  "Agrega la linea .env al archivo .gitignore y volve a correr este chequeo.")
        return
    if not archivo.exists():
        estado = PENDIENTE if offline else FALLA
        registrar(estado, "Archivo .env", "no existe",
                  "Pedile a Claude Code: preparame el entorno del taller\n"
                  "(o copia .env.example como .env y completa ANTHROPIC_API_KEY)")
        return
    if ignorado is None:
        registrar(PENDIENTE, "Archivo .env", "existe, pero sin git no puedo confirmar que este ignorado")
        return
    registrar(OK, "Archivo .env", "existe y git lo ignora")


def perfil_ant() -> bool:
    try:
        from anthropic.lib.credentials import default_credentials

        return default_credentials() is not None
    except Exception:
        return False


def chequear_key(offline: bool, en_shell: bool) -> bool:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if en_shell:
        registrar(PENDIENTE, "API key en la terminal",
                  "ANTHROPIC_API_KEY esta exportada en la shell",
                  "Sacala de la shell (la key va solo en .env). Si queda exportada, Claude Code puede usarla\n"
                  "en lugar de tu cuenta. Windows: Remove-Item Env:ANTHROPIC_API_KEY  |  macOS: unset ANTHROPIC_API_KEY")
    if not key and perfil_ant():
        registrar(OK, "API key", "sin key en .env; uso el perfil de la CLI ant (ant auth login)")
        return True
    if not key:
        registrar(PENDIENTE if offline else FALLA, "API key", "falta ANTHROPIC_API_KEY en .env",
                  "Agrega la linea ANTHROPIC_API_KEY=... en .env (la key la provee el instructor).")
        return False
    if not key.startswith("sk-ant-"):
        registrar(PENDIENTE, "API key", "presente, pero no empieza con sk-ant- (revisa que este completa)")
        return True
    registrar(OK, "API key", "presente (no se muestra)")
    return True


def chequear_api(offline: bool, hay_key: bool) -> None:
    if offline:
        registrar(PENDIENTE, "Conexion con la API", "no se verifico (--offline)")
        return
    if not hay_key:
        registrar(FALLA, "Conexion con la API", "no se puede probar sin la key")
        return
    import anthropic

    try:
        cliente = anthropic.Anthropic(timeout=30, max_retries=1)
        cliente.messages.create(model=MODELO_PRUEBA, max_tokens=5,
                                messages=[{"role": "user", "content": "Responde solo: OK"}])
        registrar(OK, "Conexion con la API", f"respondio {MODELO_PRUEBA}")
    except anthropic.AuthenticationError:
        registrar(FALLA, "Conexion con la API", "la key no es valida",
                  "Revisa que la key en .env este completa, sin espacios ni comillas.")
    except anthropic.PermissionDeniedError:
        registrar(FALLA, "Conexion con la API", "la key no tiene permiso para este modelo",
                  "Avisale al instructor.")
    except anthropic.RateLimitError:
        registrar(PENDIENTE, "Conexion con la API", "la API limito el pedido (rate limit o sin saldo)",
                  "Espera un minuto y volve a probar. Si sigue, avisale al instructor.")
    except anthropic.APIConnectionError:
        registrar(FALLA, "Conexion con la API", "no hay conexion con api.anthropic.com",
                  "Revisa la red o el proxy (ver docs/setup.md, seccion Proxy).")
    except anthropic.APIStatusError as e:
        registrar(FALLA, "Conexion con la API", f"error HTTP {e.status_code}", "Avisale al instructor.")


def chequear_polizas() -> None:
    problemas = []
    for nombre in POLIZAS:
        archivo = RAIZ / "data" / "polizas" / "txt" / f"{nombre}.txt"
        try:
            if len(archivo.read_text(encoding="utf-8")) < 1000:
                problemas.append(f"{nombre}.txt vacio")
        except OSError:
            problemas.append(f"falta {nombre}.txt")
    try:
        indice = json.loads((RAIZ / "data" / "polizas" / "clausulas.json").read_text(encoding="utf-8"))
        if not indice:
            problemas.append("clausulas.json vacio")
    except (OSError, ValueError):
        problemas.append("clausulas.json no se puede leer")
        indice = []
    if problemas:
        registrar(FALLA, "Polizas", ", ".join(problemas), "Actualiza el repo: git pull")
    else:
        registrar(OK, "Polizas", f"3 polizas en texto y {len(indice)} clausulas en el indice")


def chequear_chroma() -> None:
    try:
        import chromadb
        from chromadb.config import Settings

        cliente = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
        col = cliente.get_or_create_collection("check_setup", embedding_function=None)
        col.add(ids=["a"], embeddings=[[0.1, 0.2, 0.3]], documents=["prueba"])
        assert col.count() == 1
        registrar(OK, "Base vectorial (Chroma)", "funciona en memoria")
    except Exception as e:  # noqa: BLE001
        registrar(FALLA, "Base vectorial (Chroma)", f"{type(e).__name__}: {str(e)[:120]}",
                  "python -m pip install -r requirements.txt  (ver docs/setup.md si sigue fallando)")


def chequear_embeddings() -> None:
    try:
        from sentence_transformers import SentenceTransformer

        with silencio():
            modelo = SentenceTransformer(MODELO_EMBEDDINGS, local_files_only=True)
            vector = modelo.encode(["query: prueba"], normalize_embeddings=True, show_progress_bar=False)[0]
        registrar(OK, "Modelo de embeddings", f"{MODELO_EMBEDDINGS} en cache ({len(vector)} dimensiones)")
    except Exception as e:  # noqa: BLE001
        registrar(FALLA, "Modelo de embeddings", f"{MODELO_EMBEDDINGS} no esta descargado ({type(e).__name__})",
                  f"Descargalo una vez (necesita acceso a huggingface.co):\n{COMANDO_DESCARGA}")


def chequear_step00(offline: bool, hay_key: bool) -> None:
    if offline:
        registrar(PENDIENTE, "Step 00 (agente.py)", "no se corrio (--offline)")
        return
    if not hay_key:
        registrar(FALLA, "Step 00 (agente.py)", "no se puede correr sin la key")
        return
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        p = subprocess.run([sys.executable, str(RAIZ / "steps" / "step-00" / "agente.py")], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=180, env=entorno)
    except subprocess.TimeoutExpired:
        registrar(FALLA, "Step 00 (agente.py)", "tardo mas de 3 minutos", "Revisa la red o el proxy.")
        return
    vueltas = p.stdout.count("[vuelta")
    if p.returncode == 0 and vueltas:
        registrar(OK, "Step 00 (agente.py)", f"corrio ({vueltas} lineas de vuelta)")
    else:
        ultima = (p.stdout.strip().splitlines() or p.stderr.strip().splitlines() or ["sin salida"])[-1]
        registrar(FALLA, "Step 00 (agente.py)", ultima[:150], "Correlo a mano para ver el error completo:\n"
                  "python steps/step-00/agente.py")


def chequear_tablero(offline: bool) -> None:
    url = os.environ.get("TABLERO_URL", "").strip()
    if not url:
        registrar(PENDIENTE, "Tablero", "TABLERO_URL vacio: el avance queda guardado en tu maquina",
                  "Si el instructor proyecto TABLERO_URL y TABLERO_TOKEN, agregalos a .env.")
        return
    if offline:
        registrar(PENDIENTE, "Tablero", "no se verifico (--offline)")
        return
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            registrar(OK, "Tablero", f"responde (HTTP {r.status})")
    except urllib.error.HTTPError as e:
        registrar(PENDIENTE, "Tablero", f"responde con error HTTP {e.code}", "Revisa TABLERO_URL en .env.")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        registrar(PENDIENTE, "Tablero", f"no hay conexion ({type(e).__name__})",
                  "El proxy tiene que permitir script.google.com y script.googleusercontent.com.\n"
                  "Mientras tanto, marcar-avance guarda el avance y lo reenvia despues.")


def chequear_alias() -> None:
    archivo = RAIZ / ".taller" / "alias"
    alias = archivo.read_text(encoding="utf-8").strip() if archivo.exists() else ""
    if alias:
        registrar(OK, "Alias", alias)
    else:
        registrar(PENDIENTE, "Alias", "no hay alias en .taller/alias",
                  "Pedile a Claude Code que guarde tu alias (el nombre que aparece en el tablero).")


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description="Chequeo del entorno del taller")
    ap.add_argument("--offline", action="store_true", help="sin llamadas a la API ni a internet")
    args = ap.parse_args()

    en_shell = bool(os.environ.get("ANTHROPIC_API_KEY"))
    try:
        from dotenv import load_dotenv

        load_dotenv(RAIZ / ".env")
    except ImportError:
        pass

    print(f"Chequeo del entorno del taller ({platform.system()} {platform.release()})"
          + (" - modo offline" if args.offline else ""))
    print("-" * 70)
    chequear_python()
    librerias = chequear_librerias()
    chequear_git()
    chequear_claude_code()
    chequear_env(args.offline)
    hay_key = chequear_key(args.offline, en_shell)
    if librerias:
        chequear_api(args.offline, hay_key)
    chequear_polizas()
    if librerias:
        chequear_chroma()
        chequear_embeddings()
        chequear_step00(args.offline, hay_key)
    chequear_tablero(args.offline)
    chequear_alias()

    cuenta = {e: sum(1 for r in resultados if r[0] == e) for e in (OK, PENDIENTE, FALLA)}
    print("-" * 70)
    print(f"Resumen: {cuenta[OK]} OK, {cuenta[PENDIENTE]} PENDIENTE, {cuenta[FALLA]} FALLA")

    marca = RAIZ / ".taller" / "setup_ok"
    if cuenta[FALLA]:
        marca.unlink(missing_ok=True)
        print("Hay items en FALLA: segui el arreglo sugerido y volve a correr python check_setup.py")
        return 1
    if args.offline:
        print("Sin FALLAS en modo offline. Para marcar el entorno como listo, corre el chequeo sin --offline.")
        return 0
    marca.parent.mkdir(exist_ok=True)
    marca.write_text(json.dumps({"fecha": time.strftime("%Y-%m-%d %H:%M"), **cuenta}) + "\n", encoding="utf-8")
    print("Entorno listo. Marca el hito con: python .claude/skills/marcar-avance/marcar.py entorno_listo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
