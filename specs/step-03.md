# Spec — Step 03: construcción con Claude Code (v1)

## Objetivo

Construir con Claude Code, a partir de tu spec, una CLI que recibe una pregunta y responde con el veredicto y la cláusula citada, o dice "no sé". El flujo es: spec → plan → revisión de la pareja → implementación → iteración sobre la spec.

## Entradas

- Tu spec: `specs/asistente.md` (o la de ejemplo, con `python tools/saltar.py step-02`).
- Las tres pólizas en texto: `data/polizas/txt/hogar.txt`, `auto.txt`, `vida.txt`.
- `data/polizas/clausulas.json` para verificar que las cláusulas citadas existen.
- `data/preguntas_ejemplo.json`: las 5 preguntas que usa el tablero.
- Los prompts sugeridos: `steps/step-03/prompts.md`.

## Salidas

- `specs/plan.md`: el plan que propuso Claude Code, con la línea `Aprobado por: <alias de tu pareja>`.
- `mi-asistente/asistente.py` que respeta el contrato técnico:
  - `python mi-asistente/asistente.py "pregunta"` imprime una respuesta legible con la cita.
  - `python mi-asistente/asistente.py --json "pregunta"` imprime solo el JSON del contrato.
- La key se lee de `.env`; modelo `claude-sonnet-5-5`.

## Comportamiento esperado

- Carga las tres pólizas y responde **solo** con lo que dicen.
- Cada respuesta que afirma algo cita al menos una cláusula que existe (`documento` + `Art. N` + fragmento).
- Si la respuesta usa más de una póliza, dice de qué documento sale cada cosa.
- Si ninguna cláusula respalda la respuesta, o la pregunta está fuera de alcance, se abstiene con la frase de la spec: `veredicto: "no_sabe"`, `abstencion: true`, `citas: []`.
- Ignora el aviso de material de entrenamiento si aparece en el texto.
- Con `--json`, la salida es JSON válido aunque el modelo se equivoque de formato (por ejemplo, con salida estructurada o reintentando).

## Criterios de terminado

- [ ] Antes de las 15:45: al menos una pregunta de ejemplo respondida con una cita existente (hito `primera_cita`).
- [ ] Las 5 preguntas de `data/preguntas_ejemplo.json` responden citando la cláusula esperada (hito `ejemplos_ok`).
- [ ] Una pregunta fuera de alcance devuelve la frase de abstención y ninguna cita.
- [ ] Cuando una respuesta falló, la corregiste cambiando la spec y regenerando, no parcheando el código a mano.

## Fuera de alcance

- Búsqueda de cláusulas relevantes, bases vectoriales o embeddings: el asistente lee las tres pólizas completas.
- Tests automáticos (step 04).
- Interfaz web, servidor o canal de voz.
- Cambiar el contrato técnico.
