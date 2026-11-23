"""Step 01 · Script 3 — La misma pregunta y la misma póliza, con razonamiento.

Uso:
    python steps/step-01/03_razonamiento.py bajo
    python steps/step-01/03_razonamiento.py alto

El nivel controla el "effort": cuánto trabajo pone el modelo en toda la respuesta,
razonamiento incluido. El modelo decide solo cuándo y cuánto pensar (thinking adaptativo).
Lo que se imprime como razonamiento es un resumen: el razonamiento completo no se expone.
"""

import sys

from comun import MODELO, SYSTEM_ASISTENTE, crear_mensaje, imprimir_metricas, leer_poliza, razonamiento, texto

PREGUNTA = (
    "¿Qué cláusula de la póliza de hogar de Nación Seguros cubre la rotura de un caño "
    "y cuál es la franquicia?"
)
NIVELES = {"bajo": "low", "alto": "high"}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in NIVELES:
        print("Uso: python steps/step-01/03_razonamiento.py bajo|alto")
        sys.exit(1)
    nivel = sys.argv[1]
    pregunta = sys.argv[2] if len(sys.argv) > 2 else PREGUNTA

    contenido = f"<poliza>\n{leer_poliza('hogar')}\n</poliza>\n\nPregunta: {pregunta}"
    respuesta, segundos = crear_mensaje(
        model=MODELO,
        max_tokens=16000,
        system=SYSTEM_ASISTENTE,
        thinking={"type": "adaptive", "display": "summarized"},
        output_config={"effort": NIVELES[nivel]},
        messages=[{"role": "user", "content": contenido}],
    )

    print(f"Nivel de esfuerzo: {nivel} (effort={NIVELES[nivel]})\n")
    print("=== RAZONAMIENTO (resumen) ===")
    print(razonamiento(respuesta) or "(el modelo decidió no razonar en esta respuesta)")
    print("\n=== RESPUESTA ===")
    print(texto(respuesta))
    imprimir_metricas(respuesta, segundos)


if __name__ == "__main__":
    main()
