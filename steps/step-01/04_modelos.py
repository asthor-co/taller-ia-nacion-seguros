"""Step 01 · Script 4 (demo del instructor) — La misma pregunta con Haiku, Sonnet y Opus.

Uso:
    python steps/step-01/04_modelos.py

Muestra una tabla con costo, tiempo y el comienzo de cada respuesta.
Los tres corren con el mismo nivel de esfuerzo (medium) para que la comparación sea justa.
"""

from rich.console import Console
from rich.table import Table

from comun import MODELOS, SYSTEM_ASISTENTE, costo_usd, crear_mensaje, leer_poliza, texto

PREGUNTA = (
    "¿Qué cláusula de la póliza de hogar de Nación Seguros cubre la rotura de un caño "
    "y cuál es la franquicia?"
)


def main() -> None:
    contenido = f"<poliza>\n{leer_poliza('hogar')}\n</poliza>\n\nPregunta: {PREGUNTA}"
    tabla = Table(title="Misma pregunta, tres modelos", show_lines=True)
    tabla.add_column("Modelo")
    tabla.add_column("Tiempo (s)", justify="right")
    tabla.add_column("Tokens entrada / salida", justify="right")
    tabla.add_column("Costo (USD)", justify="right")
    tabla.add_column("Respuesta (comienzo)")

    for nombre, modelo in MODELOS.items():
        respuesta, segundos = crear_mensaje(
            model=modelo,
            max_tokens=4000,
            system=SYSTEM_ASISTENTE,
            output_config={"effort": "medium"},
            messages=[{"role": "user", "content": contenido}],
        )
        u = respuesta.usage
        resumen = " ".join(texto(respuesta).split())
        tabla.add_row(
            nombre.capitalize(),
            f"{segundos:.1f}",
            f"{u.input_tokens:,} / {u.output_tokens:,}".replace(",", "."),
            f"{costo_usd(respuesta):.4f}",
            resumen[:160] + ("…" if len(resumen) > 160 else ""),
        )
    Console().print(tabla)


if __name__ == "__main__":
    main()
