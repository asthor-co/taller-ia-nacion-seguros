# Step 05 — RAG y citas verificables (v3)

**Bloque:** 13:15–14:15 del día 2. Antes, 13:00–13:15: recap y nivelación (si no terminaste el día 1: `python tools/saltar.py step-04`).

## Qué vas a hacer

Hasta ayer, el asistente mandaba las tres pólizas completas en cada pregunta: caro, y con varias pólizas el modelo se confunde. Hoy le pasás solo las cláusulas relevantes:

1. **Chunking**: partir cada póliza en pedazos. Por cláusula (un artículo por pedazo) o por corte fijo de caracteres, que parte artículos a la mitad.
2. **Embeddings**: cada cláusula se convierte en un vector de significado con `multilingual-e5-small`. "Filtración" y "daño por agua" quedan cerca aunque no compartan palabras.
3. **Base vectorial**: Chroma guarda los vectores en tu máquina (sin servidor) y devuelve los más cercanos a la pregunta.

Spec del paso: [`specs/step-05.md`](../../specs/step-05.md). Prompts: [`prompts.md`](prompts.md).

## Pasos

1. **13:15–13:30 — Instructor**: chunking, embeddings y base vectorial.
2. **13:30–14:00 — Construcción** con los prompts 1 y 2: `mi-asistente/indexar.py` y el cambio en `asistente.py`.
3. **14:00–14:15 — Comparación** contra la versión de ayer.

## Comandos

```
python mi-asistente/indexar.py
python mi-asistente/asistente.py "Me rompieron la ventanilla del auto, que estaba cerrado con llave, y se llevaron la notebook que había dejado en el asiento. ¿Me cubre algún seguro?"
pytest mi-asistente/tests -v
python steps/step-05/comparar.py
```

`comparar.py` corre las mismas preguntas del banco contra el asistente de ayer (`checkpoints/step-04`) y contra el tuyo, y muestra tokens de entrada, costo y % de citas correctas. Con `--preguntas 8` corre menos, si falta tiempo.

## Qué mirar

- **La notebook en el auto**: la póliza de auto excluye los objetos personales dentro del vehículo; la de hogar cubre el robo de objetos fuera del domicilio, incluso desde un vehículo cerrado y forzado, con tope y denuncia policial. ¿Tu asistente cita los dos documentos y dice qué dice cada uno?
- **Tokens de entrada** en `comparar.py`: ¿cuánto bajaron? ¿Y el costo por pregunta?
- **% de citas correctas**: ¿subió, bajó o quedó igual? ¿Por qué?
- Probá `--k 1` con la pregunta de la notebook: ¿alcanza un solo fragmento?

## Para discutir con tu pareja

1. ¿Qué pasa si la cláusula que hace falta no está entre las k recuperadas?
2. ¿Por qué el corte fijo de 800 caracteres puede empeorar las citas?
3. ¿Qué otro material de tu área tendría sentido indexar así?

## Marcar el hito

```
python .claude/skills/marcar-avance/marcar.py step_05
```

Verifica que existe el índice y que una respuesta trae documento y cláusula.

## Si te atrasás

```
python tools/saltar.py step-05
python mi-asistente/indexar.py
```
