"""Step 01 · Script 1 — La trampa: una pregunta sin pasarle la póliza.

Uso:
    python steps/step-01/01_pregunta.py
    python steps/step-01/01_pregunta.py "otra pregunta"

Mirá la respuesta: ¿de dónde sacó la cláusula que cita?
"""

import sys

from comun import MODELO, SYSTEM_ASISTENTE, crear_mensaje, imprimir_metricas, texto

PREGUNTA = (
    "¿Qué cláusula de la póliza de hogar de Nación Seguros cubre la rotura de un caño "
    "y cuál es la franquicia?"
)


def main() -> None:
    pregunta = sys.argv[1] if len(sys.argv) > 1 else PREGUNTA
    respuesta, segundos = crear_mensaje(
        model=MODELO,
        max_tokens=2000,
        system=SYSTEM_ASISTENTE,
        messages=[{"role": "user", "content": pregunta}],
    )
    print(f"Pregunta: {pregunta}\n")
    print(texto(respuesta))
    imprimir_metricas(respuesta, segundos)


if __name__ == "__main__":
    main()
