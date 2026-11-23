# Spec — Step 04: Behavior Guardrails (v2)

## Objetivo

Verificar automáticamente que el asistente cumple sus reglas de comportamiento. Con un LLM no se compara la respuesta palabra por palabra (cambia entre corridas): se verifica el comportamiento, que se cumple o no.

## Entradas

- Tu asistente en `mi-asistente/asistente.py`, usado **a través del contrato** (`--json`), por subprocess.
- `data/preguntas_ejemplo.json` (preguntas que sí tienen respuesta).
- `data/preguntas_fuera_de_poliza.json` (preguntas que no tiene que responder).
- `data/polizas/clausulas.json` (las cláusulas que existen).
- Los prompts sugeridos: `steps/step-04/prompts.md`.

## Salidas

`mi-asistente/tests/test_guardrails.py` con tres guardrails, que corren con `pytest mi-asistente/tests -v`:

| Guardrail | Función | Regla |
|-----------|---------|-------|
| Siempre cita | `test_siempre_cita` | Toda respuesta a una pregunta de ejemplo trae al menos una cita con documento y artículo. |
| La cita existe | `test_cita_existe` | Cada cláusula citada está de verdad en `clausulas.json`, en el documento que dice. |
| Sabe abstenerse | `test_sabe_abstenerse` | Ante preguntas fuera de la póliza responde `no_sabe` y no cita nada. |

- Los tests llaman al asistente con `python mi-asistente/asistente.py --json ...` (ruta configurable con `ASISTENTE_CMD`), con un timeout por pregunta.
- Comparan clausulas normalizando el formato (`Art. 8`, `art 8` y `Artículo 8` son la misma).

## Criterios de terminado

- [ ] `pytest mi-asistente/tests -v` corre y muestra los tres guardrails.
- [ ] Los tres pasan en dos corridas seguidas.
- [ ] Marcaste el hito `guardrails` (se envía cuántos pasan, de 0 a 3).

## Fuera de alcance

- Medir la calidad de las respuestas con un banco de preguntas: eso es evaluación, y queda para el día 2.
- Cambiar el contrato técnico para que los tests pasen.
