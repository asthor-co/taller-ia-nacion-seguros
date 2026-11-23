# Step 03 — Construcción con Claude Code (v1)

**Bloque:** 15:15–16:30 del día 1.

## Qué vas a hacer

Pasar de tu spec a una CLI que responde con la cláusula citada, sin escribir el código a mano. El flujo:

```
spec  ->  plan (modo plan)  ->  revisión de la pareja  ->  implementación  ->  iteración sobre la spec
```

Spec del paso: [`specs/step-03.md`](../../specs/step-03.md). Los prompts para copiar y pegar están en [`prompts.md`](prompts.md).

## Pasos

1. **15:15–15:25 — Demo del instructor** con un ejemplo chico que no es el asistente.
2. **15:25–15:40 — El plan.** En Claude Code, activá el modo plan (Shift+Tab hasta que abajo diga *plan mode*) y pegá el prompt 1 de `prompts.md`. Claude Code propone un plan sin tocar archivos. Tu pareja lo lee y lo revisa con las preguntas de `prompts.md`. Cuando está aprobado, pegá el prompt 2: guarda el plan en `specs/plan.md` con la línea `Aprobado por: <alias de tu pareja>`.
3. **15:40–16:15 — Implementación.** Salí del modo plan y pegá el prompt 3. Claude Code escribe `mi-asistente/asistente.py` y prueba las 5 preguntas de ejemplo.
4. **Victoria temprana: antes de las 15:45** tenés que tener al menos una respuesta correcta con cita. Marcá `primera_cita`.
5. **16:15–16:25 — Iteración.** Si una respuesta falla, **corregí la spec, no el código**, y pedí que se regenere (prompt 4).
6. **16:25–16:30 — Los gerentes preguntan.** Cada gerente le hace una pregunta difícil a tu asistente.

## Comandos

```
python mi-asistente/asistente.py "Explotó el calefón y rompió la pared del lavadero, pero no hubo fuego. ¿Está cubierto?"
python mi-asistente/asistente.py --json "¿A cuánto está el dólar oficial hoy?"
```

La primera tiene que responder con veredicto y cita. La segunda, con la frase de abstención y `"citas": []`.

## Qué mirar

- ¿El plan respeta tu spec, o agrega cosas que no pediste? Un plan con cosas de más es código de más para revisar.
- Con `--json`, ¿la salida es **solo** el JSON? Si imprime algo más, el tablero y los guardrails no lo pueden leer.
- Abrí `data/polizas/txt/` y verificá que la cita dice lo que el asistente afirma.
- Mirá los tokens y el costo de cada respuesta: van las tres pólizas completas en cada pregunta. La primera paga la escritura en la caché; las siguientes, dentro de los 5 minutos, leen las pólizas de la caché y cuestan bastante menos.

## Para discutir con tu pareja

1. ¿Qué cambio en la spec arregló más respuestas? ¿Por qué es mejor corregir la spec que el código?
2. La pregunta del gerente: ¿la respondió bien? ¿Se abstuvo cuando correspondía?
3. ¿Qué parte del código no entendés? Pedile a Claude Code que te la explique.

## Marcar los hitos

```
python .claude/skills/marcar-avance/marcar.py plan_aprobado
python .claude/skills/marcar-avance/marcar.py primera_cita
python .claude/skills/marcar-avance/marcar.py ejemplos_ok
```

`ejemplos_ok` pide que las 5 preguntas de `data/preguntas_ejemplo.json` citen la cláusula esperada.

## Si te atrasás

Si a las 15:45 no tenés ninguna respuesta con cita, saltá al checkpoint y seguí desde ahí:

```
python tools/saltar.py step-03
```

Tu trabajo queda en `mi-asistente.backup-<hora>/`. Podés comparar los dos con Claude Code: "comparame mi-asistente con mi backup y explicame la diferencia".
