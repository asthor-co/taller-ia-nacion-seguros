"""Step 00 (opcional) — Un agente mínimo: modelo + herramientas + loop.

Uso:
    python steps/step-00/agente.py
    python steps/step-00/agente.py "¿La póliza de auto cubre el remolque?"

Esto es, en chiquito, lo que hacen Claude Code o un agente de voz: el modelo pide
herramientas, el programa las ejecuta y le devuelve el resultado, hasta que el modelo responde.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "step-01"))
from comun import MODELO, crear_mensaje, leer_poliza, texto  # noqa: E402

HERRAMIENTAS = [
    {
        "name": "leer_poliza",
        "description": "Devuelve el texto completo de una póliza: hogar, auto o vida.",
        "input_schema": {
            "type": "object",
            "properties": {"nombre": {"type": "string", "enum": ["hogar", "auto", "vida"]}},
            "required": ["nombre"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "name": "buscar_clausula",
        "description": "Busca una palabra en una póliza y devuelve los artículos que la mencionan.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nombre": {"type": "string", "enum": ["hogar", "auto", "vida"]},
                "palabra": {"type": "string"},
            },
            "required": ["nombre", "palabra"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def ejecutar(nombre: str, args: dict) -> str:
    if nombre == "leer_poliza":
        return leer_poliza(args["nombre"])
    articulos = leer_poliza(args["nombre"]).split("\n\nArt. ")
    hallados = ["Art. " + a for a in articulos if args["palabra"].lower() in a.lower()]
    return "\n\n".join(hallados[:5]) or "No encontré artículos con esa palabra."


def main() -> None:
    pregunta = sys.argv[1] if len(sys.argv) > 1 else "¿La póliza de auto cubre el remolque? ¿Cuántos kilómetros?"
    mensajes = [{"role": "user", "content": pregunta}]
    for vuelta in range(1, 11):
        respuesta, _ = crear_mensaje(model=MODELO, max_tokens=4000, tools=HERRAMIENTAS, messages=mensajes)
        mensajes.append({"role": "assistant", "content": respuesta.content})
        pedidos = [b for b in respuesta.content if b.type == "tool_use"]
        if respuesta.stop_reason != "tool_use" or not pedidos:
            print(f"[vuelta {vuelta}] el modelo terminó\n")
            print(texto(respuesta))
            return
        resultados = []
        for pedido in pedidos:
            print(f"[vuelta {vuelta}] herramienta={pedido.name} args={json.dumps(pedido.input, ensure_ascii=False)}")
            resultados.append({"type": "tool_result", "tool_use_id": pedido.id, "content": ejecutar(pedido.name, pedido.input)})
        mensajes.append({"role": "user", "content": resultados})
    print("Corté después de 10 vueltas.")


if __name__ == "__main__":
    main()
