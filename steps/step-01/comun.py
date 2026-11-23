"""Utilidades comunes del step 01: cliente de la API, precios y métricas.

Todos los scripts del step usan el mismo modelo, así todas las mesas ven los mismos números.

Variables de entorno (en el archivo .env de la raíz del repo):
    ANTHROPIC_API_KEY   la key de la API de Anthropic (la provee Nación Seguros).

Opcionales, para el instructor:
    TALLER_CACHE=record   guarda cada respuesta en .cache/ (para reproducirla sin red).
    TALLER_CACHE=replay   responde desde .cache/ sin llamar a la API.
    TALLER_CACHE_DIR      carpeta de la caché (por defecto .cache/ en la raíz del repo).
    TALLER_LEDGER         archivo .jsonl donde se registra el gasto de cada llamada.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import anthropic
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")

MODELO = "claude-sonnet-5-5"
MODELOS = {
    "haiku": "claude-haiku-5-5",
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
}

# Precios en USD por millón de tokens.
# Fuente: https://platform.claude.com/docs/en/about-claude/pricing (consultada el 21/11/2026).
# Haiku 5.5: estos precios valen para prompts de hasta 100.000 tokens; por encima, 0,50 / 2,50.
PRECIOS = {
    "claude-haiku-5-5": {"entrada": 0.10, "salida": 0.50, "cache_escritura": 0.125, "cache_lectura": 0.01},
    "claude-sonnet-5-5": {"entrada": 2.00, "salida": 10.00, "cache_escritura": 2.50, "cache_lectura": 0.10},
    "claude-opus-5-5": {"entrada": 4.00, "salida": 20.00, "cache_escritura": 5.00, "cache_lectura": 0.20},
}
PRECIOS_HAIKU_LARGO = {"entrada": 0.50, "salida": 2.50, "cache_escritura": 0.625, "cache_lectura": 0.05}

SYSTEM_ASISTENTE = "Sos el asistente virtual de atención al cliente de Nación Seguros."


def _cache_dir() -> Path:
    return Path(os.environ.get("TALLER_CACHE_DIR") or RAIZ / ".cache")


def _serializable(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json", exclude_none=True)
    return str(obj)


def _clave(params: dict) -> str:
    crudo = json.dumps(params, sort_keys=True, ensure_ascii=False, default=_serializable)
    return hashlib.sha256(crudo.encode("utf-8")).hexdigest()[:20]


def hay_credenciales() -> bool:
    """API key en .env, o un perfil de la CLI `ant` (ant auth login) que el SDK encuentra solo."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return True
    try:
        from anthropic.lib.credentials import default_credentials

        return default_credentials() is not None
    except Exception:
        return False


def cliente() -> anthropic.Anthropic:
    if not hay_credenciales():
        print("Falta la API key. Creá el archivo .env en la raíz del repo con la línea:")
        print("    ANTHROPIC_API_KEY=tu-key")
        print("(o pedile a Claude Code: \"preparame el entorno del taller\")")
        sys.exit(1)
    return anthropic.Anthropic(max_retries=4)


def crear_mensaje(**params) -> tuple[anthropic.types.Message, float]:
    """Llama a la API (o a la caché) y devuelve (respuesta, segundos)."""
    modo = os.environ.get("TALLER_CACHE", "off")
    archivo = _cache_dir() / f"{_clave(params)}.json"
    if modo == "replay":
        if not archivo.exists():
            print(f"No hay respuesta grabada para esta llamada ({archivo.name}). Corré con TALLER_CACHE=record primero.")
            sys.exit(1)
        guardado = json.loads(archivo.read_text(encoding="utf-8"))
        return anthropic.types.Message.model_validate(guardado["respuesta"]), guardado["segundos"]

    t0 = time.perf_counter()
    try:
        respuesta = cliente().messages.create(**params)
    except anthropic.AuthenticationError:
        print("La API key no es válida. Revisá el archivo .env.")
        sys.exit(1)
    except anthropic.RateLimitError:
        print("La API está limitando la cantidad de pedidos. Esperá unos segundos y volvé a probar.")
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("No hay conexión con api.anthropic.com. Revisá la red o el proxy.")
        sys.exit(1)
    segundos = time.perf_counter() - t0

    if modo == "record":
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text(
            json.dumps({"respuesta": respuesta.model_dump(mode="json"), "segundos": segundos}, ensure_ascii=False),
            encoding="utf-8",
        )
    _registrar_gasto(respuesta, segundos)
    return respuesta, segundos


def costo_usd(respuesta: anthropic.types.Message) -> float:
    u = respuesta.usage
    escritura = u.cache_creation_input_tokens or 0
    lectura = u.cache_read_input_tokens or 0
    clave = next((k for k in PRECIOS if respuesta.model.startswith(k)), MODELO)
    precios = PRECIOS[clave]
    if clave == "claude-haiku-5-5" and u.input_tokens + escritura + lectura > 100_000:
        precios = PRECIOS_HAIKU_LARGO
    return (
        u.input_tokens * precios["entrada"]
        + escritura * precios["cache_escritura"]
        + lectura * precios["cache_lectura"]
        + u.output_tokens * precios["salida"]
    ) / 1_000_000


def _registrar_gasto(respuesta: anthropic.types.Message, segundos: float) -> None:
    destino = os.environ.get("TALLER_LEDGER")
    if not destino:
        return
    u = respuesta.usage
    fila = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "script": Path(sys.argv[0]).name,
        "modelo": respuesta.model,
        "entrada": u.input_tokens,
        "salida": u.output_tokens,
        "cache_lectura": u.cache_read_input_tokens or 0,
        "cache_escritura": u.cache_creation_input_tokens or 0,
        "costo_usd": round(costo_usd(respuesta), 6),
        "segundos": round(segundos, 2),
    }
    with open(destino, "a", encoding="utf-8") as f:
        f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def texto(respuesta: anthropic.types.Message) -> str:
    return "\n".join(b.text for b in respuesta.content if b.type == "text").strip()


def razonamiento(respuesta: anthropic.types.Message) -> str:
    return "\n".join(b.thinking for b in respuesta.content if b.type == "thinking").strip()


def leer_poliza(nombre: str = "hogar", con_footer: bool = False) -> str:
    archivo = f"{nombre}_con_footer.txt" if con_footer else f"{nombre}.txt"
    return (RAIZ / "data" / "polizas" / "txt" / archivo).read_text(encoding="utf-8")


def imprimir_metricas(respuesta: anthropic.types.Message, segundos: float) -> None:
    u = respuesta.usage
    print("-" * 60)
    print(f"Modelo:             {respuesta.model}")
    print(f"Tokens de entrada:  {u.input_tokens + (u.cache_read_input_tokens or 0) + (u.cache_creation_input_tokens or 0):,}".replace(",", "."))
    print(f"Tokens de salida:   {u.output_tokens:,}".replace(",", "."))
    print(f"Costo:              USD {costo_usd(respuesta):.4f}")
    print(f"Tiempo:             {segundos:.1f} s")
    print("-" * 60)


def guardar_salida(nombre: str, contenido: str) -> None:
    """Deja una copia de la salida en .taller/ (la usa el skill marcar-avance)."""
    carpeta = RAIZ / ".taller"
    carpeta.mkdir(exist_ok=True)
    (carpeta / nombre).write_text(contenido, encoding="utf-8")
