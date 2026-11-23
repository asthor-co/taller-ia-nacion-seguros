# Step 04 — Behavior Guardrails (v2)

**Bloque:** 16:30–16:50 del día 1.

## Qué vas a hacer

Pedirle a Claude Code tres **Behavior Guardrails**: reglas de comportamiento que se verifican solas y se cumplen o no. No se llaman tests de respuesta porque con un LLM no se compara palabra por palabra (la respuesta cambia entre corridas): se verifica el comportamiento.

| Guardrail | Regla |
|-----------|-------|
| Siempre cita | Toda respuesta trae una cita con el formato acordado. |
| La cita existe | La cláusula citada está de verdad en el documento. |
| Sabe abstenerse | Ante preguntas fuera de la póliza, responde que no sabe. |

Spec del paso: [`specs/step-04.md`](../../specs/step-04.md). Los prompts están en [`prompts.md`](prompts.md).

## Pasos

1. **16:30–16:35 — Instructor**: por qué se verifica el comportamiento y no el texto.
2. **16:35–16:50 — Práctica**: pegá el prompt de `prompts.md`, corré los guardrails y marcá cuántos pasan.

## Comandos

```
pytest mi-asistente/tests -v
```

(si `pytest` no se encuentra: `python -m pytest mi-asistente/tests -v`). Hace unas 10 preguntas al asistente: tarda uno o dos minutos.

## Qué mirar

- Las preguntas fuera de póliza están en `data/preguntas_fuera_de_poliza.json`: el dólar, otra aseguradora, los datos de un asegurado puntual, un producto que no existe. ¿Cuál le cuesta más a tu asistente?
- Si un guardrail falla, leé el mensaje: dice qué pregunta y por qué. Antes de tocar el test, preguntate si la regla está bien escrita en tu spec.
- Corré los guardrails dos veces seguidas. ¿Dan lo mismo? Si no, ¿qué te dice eso del asistente?

## Para discutir con tu pareja

1. ¿Qué cosas importantes de una respuesta **no** verifican estos tres guardrails?
2. Si los tres pasan, ¿podés confiar en todo lo que responde el asistente?
3. ¿Qué otro guardrail agregarías para tu área?

## Marcar el hito

```
python .claude/skills/marcar-avance/marcar.py guardrails
```

Envía cuántos de los tres pasan (0 a 3). Podés volver a marcarlo cuando mejores.

## Si te atrasás

El checkpoint trae el asistente v1 y los tres guardrails listos:

```
python tools/saltar.py step-04
pytest mi-asistente/tests -v
```

Este es también el punto de partida del día 2: si no terminaste hoy, mañana empezás desde acá.
