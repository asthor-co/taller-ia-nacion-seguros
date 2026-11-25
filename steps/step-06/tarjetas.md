# Tarjetas de experimento — Step 06

Cada pareja recibe una tarjeta. Cada integrante prueba **una** de las dos variantes (A o B) y la compara contra su puntaje base. Una palanca por persona: si cambiás dos cosas a la vez, no sabés cuál produjo el efecto.

Antes de cualquier variante, corré tu base: `python steps/step-06/evaluar.py --rapido`. Base y variante, siempre con `--rapido`: así corren las mismas 20 preguntas y se pueden comparar.

El juez queda fijo (Sonnet) en todas las corridas, también cuando la palanca es el modelo o el effort. Así lo que cambia es tu asistente, no quien lo corrige.

Si falta tiempo, agregá `--rapido` a cualquier comando (20 preguntas).

---

## Tarjeta 1 — Redacción de la spec: la regla de abstención

**Hipótesis:** una regla de abstención más exigente sube la abstención correcta, pero puede hacer que se abstenga en preguntas que sí tienen respuesta.

| | Qué cambiar | Comando |
|---|---|---|
| A | La regla estricta del checkpoint: ante la menor duda, se abstiene. | `python steps/step-06/evaluar.py --rapido --variante "abstencion-estricta" --args "--abstencion estricta"` |
| B | Reescribí vos la regla de abstención en `specs/asistente.md` (por ejemplo, con dos ejemplos de zona gris) y pedile a Claude Code que regenere el prompt. | `python steps/step-06/evaluar.py --rapido --variante "abstencion-spec"` |

**Qué medir:** abstención correcta, y cuántas abstenciones indebidas aparecen en la lista de fallas ("se abstuvo en una pregunta que sí tiene respuesta").

## Tarjeta 2 — Chunking: por cláusula contra corte fijo

**Hipótesis:** cortar cada 800 caracteres parte artículos a la mitad y empeora la cita correcta.

Antes: `python mi-asistente/indexar.py --chunking fijo` (crea el índice con cortes fijos).

| | Qué cambiar | Comando |
|---|---|---|
| A | Corte fijo de 800 caracteres. | `python steps/step-06/evaluar.py --rapido --variante "chunking-fijo" --args "--chunking fijo"` |
| B | Corte fijo, pero recuperando más fragmentos para compensar. | `python steps/step-06/evaluar.py --rapido --variante "chunking-fijo-k10" --args "--chunking fijo --k 10"` |

**Qué medir:** cita correcta y acierto en las preguntas de exclusiones escondidas.

## Tarjeta 3 — Cláusulas recuperadas: 3 contra 10

**Hipótesis:** con pocas cláusulas falta contexto (sobre todo en preguntas que mezclan pólizas); con muchas, sube el costo y entra ruido.

| | Qué cambiar | Comando |
|---|---|---|
| A | 3 cláusulas. | `python steps/step-06/evaluar.py --rapido --variante "k=3" --args "--k 3"` |
| B | 10 cláusulas. | `python steps/step-06/evaluar.py --rapido --variante "k=10" --args "--k 10"` |

**Qué medir:** acierto en las preguntas de contradicción y multi-documento, y costo total de la corrida.

## Tarjeta 4 — Modelo: Haiku contra Sonnet

**Hipótesis:** un modelo más chico es mucho más barato y rápido; la pregunta es cuánto pierde en las preguntas difíciles.

| | Qué cambiar | Comando |
|---|---|---|
| A | Haiku. | `python steps/step-06/evaluar.py --rapido --variante "modelo-haiku" --args "--modelo haiku"` |
| B | Opus (el más grande). | `python steps/step-06/evaluar.py --rapido --variante "modelo-opus" --args "--modelo opus"` |

**Qué medir:** puntaje, costo y minutos de la corrida, comparados con tu base (Sonnet).

## Tarjeta 5 — Effort: bajo contra alto

**Hipótesis:** menos esfuerzo responde más rápido y más barato, y falla más en las ambiguas.

| | Qué cambiar | Comando |
|---|---|---|
| A | Effort bajo. | `python steps/step-06/evaluar.py --rapido --variante "effort-low" --args "--effort low"` |
| B | Effort medio. | `python steps/step-06/evaluar.py --rapido --variante "effort-medium" --args "--effort medium"` |

Tu base corre con effort alto (`high`).

**Qué medir:** acierto en las preguntas ambiguas (`depende`) y de límites y montos; costo y minutos.

## Tarjeta 6 — Ejemplos de preguntas y respuestas en el prompt

**Hipótesis:** mostrarle al modelo ejemplos resueltos mejora el formato y el criterio, a cambio de más tokens de entrada.

| | Qué cambiar | Comando |
|---|---|---|
| A | Suma al prompt las 5 preguntas de ejemplo con su respuesta. | `python steps/step-06/evaluar.py --rapido --variante "ejemplos" --args "--ejemplos"` |
| B | Ejemplos con un modelo chico: ¿compensan? | `python steps/step-06/evaluar.py --rapido --variante "ejemplos-haiku" --args "--ejemplos --modelo haiku"` |

**Qué medir:** acierto y cita correcta; costo por pregunta.

## Tarjeta 7 — Razonar antes de citar contra responder directo

**Hipótesis:** razonar antes de responder mejora las preguntas con trampa; responder directo es más rápido y barato.

| | Qué cambiar | Comando |
|---|---|---|
| A | Sin razonamiento previo. | `python steps/step-06/evaluar.py --rapido --variante "razonar-no" --args "--razonar no"` |
| B | Sin razonamiento y con effort bajo (lo más rápido posible). | `python steps/step-06/evaluar.py --rapido --variante "razonar-no-effort-low" --args "--razonar no --effort low"` |

Tu base razona (`--razonar si`).

**Qué medir:** acierto en exclusiones escondidas y ambiguas; minutos de la corrida.

---

## Cómo reportar

1. El puntaje se envía solo al tablero (si no hay conexión, queda en `.taller/pendientes.jsonl`).
2. Marcá el hito: `python .claude/skills/marcar-avance/marcar.py eval_variante`.
3. Para la demo de las 15:50, preparen en una frase: qué palanca probaron, cuánto cambió el puntaje (y el costo) y si el cambio es mayor que la variación entre dos corridas iguales.
