# Step 04 — Prompts sugeridos

## Prompt 1 — Los tres guardrails

```
Creá mi-asistente/tests/test_guardrails.py con pytest, con tres Behavior Guardrails basados en mi spec
(specs/asistente.md). Los tests no comparan texto: verifican comportamiento.

Reglas generales:
- Llamá al asistente solo a través del contrato: python mi-asistente/asistente.py --json "<pregunta>",
  con subprocess, desde la raíz del repo, con timeout de 120 segundos por pregunta y encoding utf-8.
  Si existe la variable de entorno ASISTENTE_CMD, usala como comando en lugar de ese.
- Si la salida no es JSON válido, el test falla con un mensaje claro.
- Al comparar cláusulas, normalizá el número de artículo ("Art. 8", "art 8" y "Artículo 8" son la misma).
- No uses librerías fuera de requirements.txt.

Los tres guardrails, con estos nombres exactos:
1. test_siempre_cita: para cada pregunta de data/preguntas_ejemplo.json, la respuesta trae al menos
   una cita con documento y número de artículo.
2. test_cita_existe: para esas mismas respuestas, cada cita existe en data/polizas/clausulas.json
   (mismo documento y mismo artículo). Reusá las respuestas del test 1 (no vuelvas a preguntar).
3. test_sabe_abstenerse: para las primeras 5 preguntas de data/preguntas_fuera_de_poliza.json,
   la respuesta tiene abstencion true o veredicto "no_sabe", y no trae citas.

Cuando termines, corré: python -m pytest mi-asistente/tests -v
y explicame el resultado en tres líneas.
```

## Prompt 2 — Si un guardrail falla

Primero, la spec:

```
El guardrail <nombre> falló con este mensaje: <mensaje>.
No toques el test ni el código todavía. Decime si el problema es de la spec (la regla no está clara
o falta), del asistente (no cumple la spec) o del test (verifica algo que la spec no pide).
```

Si es la spec: corregila y regenerá, como en el step 03. Si es el test, que lo ajuste a lo que dice la spec, nunca al revés.

## Prompt 3 — Entender los guardrails

```
Explicame mi-asistente/tests/test_guardrails.py para alguien que no programa:
qué verifica cada guardrail y qué no verifica.
```

Marcá el hito: `python .claude/skills/marcar-avance/marcar.py guardrails`.
