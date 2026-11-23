# Step 02 — La spec del asistente

**Bloque:** 14:45–15:15 del día 1.

## Qué vas a hacer

Escribir la spec de tu Asistente de Coberturas con el skill `escribir-spec`, que te entrevista. Las decisiones son tuyas: qué responde y qué no, qué fuentes usa, cómo cita y qué dice cuando no sabe. Una spec dice cosas que se pueden verificar ("responde en 4 oraciones como máximo"), no deseos ("responde bien").

Spec del paso: [`specs/step-02.md`](../../specs/step-02.md).

## Pasos

1. **14:45–14:55 — Prompt vs. spec** (instructor).
2. **14:55–15:10 — Entrevista.** En Claude Code, pedí:

   > Usá el skill escribir-spec para armar la spec de mi asistente.

   El skill te pide, en orden: material de contexto (solo público o anonimizado, **nunca datos de asegurados**), qué responde y qué no, el formato de la cita, qué hacer cuando no hay cláusula que respalde, y de 3 a 5 preguntas de ejemplo con su respuesta esperada. Al final guarda `specs/asistente.md`.

3. **15:10–15:15 — Revisión.** Tu pareja revisa tu spec con [`.claude/skills/escribir-spec/checklist.md`](../../.claude/skills/escribir-spec/checklist.md) y la comparan con [`specs/ejemplo-asistente.md`](../../specs/ejemplo-asistente.md).

## Qué mirar

- La última sección, "Contrato técnico (no modificar)", queda igual que en la plantilla. De ahí dependen el tablero y los guardrails.
- Buscá las cláusulas de tus ejemplos en `data/polizas/txt/`: si el ejemplo dice "Art. 22", que el Art. 22 diga eso.
- ¿Tu regla de abstención tiene una frase exacta? Si no, cada respuesta va a decir "no sé" de una forma distinta.

## Para discutir con tu pareja

1. ¿Qué decidió distinto la spec de ejemplo? ¿Te sirve alguna de sus decisiones?
2. ¿Qué pregunta de un cliente real quedaría en una zona gris de tu alcance?
3. ¿Qué es peor para el negocio: un "no sé" de más o una respuesta inventada?

## Marcar el hito

Cuando tu pareja tildó los 8 ítems del checklist:

```
python .claude/skills/marcar-avance/marcar.py spec
```

## Si te atrasás

Usá la spec de ejemplo y seguí con el step 03:

```
python tools/saltar.py step-02
```

Deja la spec de ejemplo en `specs/asistente.md` (si ya tenías una, queda respaldada). Cambiale el autor y la fecha y marcá el hito.
