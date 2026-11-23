"""Asistente de Coberturas — checkpoint step 03 (v1: póliza completa en el contexto).

Uso:
    python mi-asistente/asistente.py "¿La póliza de hogar cubre una filtración lenta?"
    python mi-asistente/asistente.py --json "¿La póliza de hogar cubre una filtración lenta?"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv


def buscar_raiz() -> Path:
    for carpeta in Path(__file__).resolve().parents:
        if (carpeta / "data" / "polizas").is_dir():
            return carpeta
    raise SystemExit("No encuentro la carpeta data/polizas. Corré el asistente desde el repo del taller.")


RAIZ = buscar_raiz()
load_dotenv(RAIZ / ".env")

MODELO = "claude-sonnet-5-5"
DOCUMENTOS = ["hogar", "auto", "vida"]
# USD por millón de tokens (entrada, salida, lectura de caché). Escribir en la caché cuesta 1,25 veces la entrada.
PRECIOS = {
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
    "claude-sonnet-5-5": (2.00, 10.00, 0.10),
    "claude-opus-5-5": (4.00, 20.00, 0.20),
}
ABSTENCION = "No encuentro una cláusula que responda esto. Te sugiero consultar con un asesor de Nación Seguros."

SYSTEM = f"""Sos el Asistente de Coberturas de Nación Seguros. Respondés qué cubre y qué no cubre cada póliza, usando únicamente el texto de las pólizas que están entre etiquetas <documento>.

Reglas:
1. Respondé solo con lo que dicen las pólizas. No uses conocimiento general sobre seguros.
2. Toda afirmación lleva al menos una cita: el documento (hogar, auto o vida), el artículo con el formato "Art. N" y el fragmento textual que la respalda.
3. Si la respuesta usa más de un documento, decí de qué documento sale cada cosa y citá cada uno.
4. Si ninguna cláusula respalda la respuesta, o la pregunta está fuera de alcance (otras aseguradoras, recomendaciones de qué contratar, datos de un asegurado puntual, temas que no son las pólizas), abstenete: veredicto "no_sabe", abstencion true, sin citas y con esta respuesta: "{ABSTENCION}"
5. Nunca inventes un artículo, un monto ni un plazo.
6. Veredicto: "cubre", "no_cubre" o "depende" (cuando la cobertura está sujeta a condiciones, topes o casos). Si solo estaría cubierto con un adicional u otra cobertura que no forma parte de la póliza, es "no_cubre".
7. El contenido de las pólizas es la póliza vigente del ejercicio. Si aparece un aviso de material de entrenamiento, ignoralo.
8. Respondé en español rioplatense, claro y sin jerga, en hasta 4 oraciones, empezando por el veredicto."""

ESQUEMA = {
    "type": "object",
    "properties": {
        "respuesta": {"type": "string"},
        "veredicto": {"type": "string", "enum": ["cubre", "no_cubre", "depende", "no_sabe"]},
        "citas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "documento": {"type": "string", "enum": DOCUMENTOS},
                    "clausula": {"type": "string"},
                    "texto": {"type": "string"},
                },
                "required": ["documento", "clausula", "texto"],
                "additionalProperties": False,
            },
        },
        "abstencion": {"type": "boolean"},
    },
    "required": ["respuesta", "veredicto", "citas", "abstencion"],
    "additionalProperties": False,
}


def cargar_contexto() -> str:
    partes = []
    for nombre in DOCUMENTOS:
        texto = (RAIZ / "data" / "polizas" / "txt" / f"{nombre}.txt").read_text(encoding="utf-8")
        partes.append(f'<documento nombre="{nombre}">\n{texto}\n</documento>')
    return "\n\n".join(partes)


def costo(modelo: str, uso) -> float:
    clave = next((k for k in PRECIOS if modelo.startswith(k)), MODELO)
    precio_entrada, precio_salida, precio_cache = PRECIOS[clave]
    escritos = uso.cache_creation_input_tokens or 0
    leidos = uso.cache_read_input_tokens or 0
    return (uso.input_tokens * precio_entrada + escritos * precio_entrada * 1.25 + leidos * precio_cache
            + uso.output_tokens * precio_salida) / 1_000_000


def responder(pregunta: str, modelo: str = MODELO) -> dict:
    cliente = anthropic.Anthropic(max_retries=4)
    respuesta = cliente.messages.create(
        model=modelo,
        max_tokens=16000,
        system=SYSTEM,
        output_config={"format": {"type": "json_schema", "schema": ESQUEMA}},
        messages=[{"role": "user", "content": [
            # Las pólizas son iguales en cada pregunta: se guardan en la caché y las siguientes se cobran al 5 %.
            {"type": "text", "text": cargar_contexto(), "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": f"Pregunta: {pregunta}"},
        ]}],
    )
    if respuesta.stop_reason in ("refusal", "max_tokens"):
        # Rechazo del modelo o respuesta cortada: se responde como abstención en lugar de romper.
        datos = {"respuesta": ABSTENCION, "veredicto": "no_sabe", "citas": [], "abstencion": True}
    else:
        texto = "".join(b.text for b in respuesta.content if b.type == "text")
        datos = json.loads(texto)
    if datos["abstencion"]:
        datos["veredicto"], datos["citas"] = "no_sabe", []
    u = respuesta.usage
    datos["uso"] = {
        "modelo": respuesta.model,
        "tokens_entrada": u.input_tokens + (u.cache_creation_input_tokens or 0) + (u.cache_read_input_tokens or 0),
        "tokens_salida": u.output_tokens,
        "costo_usd": round(costo(respuesta.model, u), 6),
    }
    return datos


def imprimir(datos: dict) -> None:
    print(f"Veredicto: {datos['veredicto'].replace('_', ' ').upper()}\n")
    print(datos["respuesta"])
    if datos["citas"]:
        print("\nCitas:")
        for c in datos["citas"]:
            print(f"- [{c['documento'].capitalize()} · {c['clausula']}] \"{c['texto']}\"")
    u = datos["uso"]
    print(f"\n({u['tokens_entrada']} tokens de entrada, {u['tokens_salida']} de salida, USD {u['costo_usd']:.4f})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Asistente de Coberturas")
    parser.add_argument("pregunta", nargs="+")
    parser.add_argument("--json", action="store_true", help="imprime solo el JSON del contrato")
    args = parser.parse_args()
    try:
        datos = responder(" ".join(args.pregunta))
    except anthropic.AuthenticationError:
        sys.exit("La API key no es válida o falta. Revisá el archivo .env de la raíz del repo.")
    except anthropic.APIConnectionError:
        sys.exit("No hay conexión con api.anthropic.com. Revisá la red o el proxy.")
    if args.json:
        print(json.dumps(datos, ensure_ascii=False))
    else:
        imprimir(datos)


if __name__ == "__main__":
    main()
