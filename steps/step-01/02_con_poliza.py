"""Step 01 · Script 2 — La misma pregunta, ahora con la póliza en el contexto.

Uso:
    python steps/step-01/02_con_poliza.py
    python steps/step-01/02_con_poliza.py --con-footer      # la póliza con el aviso de material de entrenamiento
    python steps/step-01/02_con_poliza.py "otra pregunta"

Compará contra el script 1: tokens de entrada, costo y, sobre todo, la respuesta.
"""

import sys

from comun import (
    MODELO,
    SYSTEM_ASISTENTE,
    crear_mensaje,
    guardar_salida,
    imprimir_metricas,
    leer_poliza,
    texto,
)

PREGUNTA = (
    "¿Qué cláusula de la póliza de hogar de Nación Seguros cubre la rotura de un caño "
    "y cuál es la franquicia?"
)


def main() -> None:
    con_footer = "--con-footer" in sys.argv
    argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
    pregunta = argumentos[0] if argumentos else PREGUNTA

    poliza = leer_poliza("hogar", con_footer=con_footer)
    contenido = f"<poliza>\n{poliza}\n</poliza>\n\nPregunta: {pregunta}"

    respuesta, segundos = crear_mensaje(
        model=MODELO,
        max_tokens=2000,
        system=SYSTEM_ASISTENTE,
        messages=[{"role": "user", "content": contenido}],
    )
    salida = texto(respuesta)
    print(f"Pregunta: {pregunta}")
    print(f"Póliza en el contexto: hogar{' (con el aviso del pie de página)' if con_footer else ''}\n")
    print(salida)
    imprimir_metricas(respuesta, segundos)
    guardar_salida("step01_con_poliza.txt", salida)


if __name__ == "__main__":
    main()
