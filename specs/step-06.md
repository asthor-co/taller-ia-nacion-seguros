# Spec — Step 06: evaluación (v4)

## Objetivo

Medir la calidad del asistente con un banco de preguntas común y comparar, con números, el efecto de una palanca. Los guardrails verifican reglas; las evals miden calidad.

## Entradas

- Tu asistente v3 en `mi-asistente/` (o `python tools/saltar.py step-05`).
- `data/banco_preguntas.json`: 59 preguntas con veredicto, respuesta y cláusulas correctas, de varios tipos (directas, exclusiones escondidas, ambiguas, entre documentos, límites y montos, plazos, fuera de póliza).
- `steps/step-06/evaluar.py` (ya escrito) y las tarjetas de experimento (`steps/step-06/tarjetas.md`).

## Salidas

- Un puntaje base: `python steps/step-06/evaluar.py --rapido` (20 preguntas, siempre las mismas).
- Un puntaje con la variante de tu tarjeta: `python steps/step-06/evaluar.py --rapido --variante "<nombre>" --args "<flags>"`.
- Para cada corrida, `resultados/<alias>-<variante>-<hora>.json`.

Métricas:

| Métrica | Cómo se mide |
|---------|--------------|
| Acierto | Otro modelo (LLM como juez) compara veredicto y respuesta contra la esperada. |
| Cita correcta | Sin modelo: alguna cláusula citada está entre las correctas. |
| Abstención correcta | Ante preguntas fuera de la póliza, dice que no sabe. |

Para probar las palancas, tu asistente acepta (además del contrato) los flags de tu tarjeta: `--abstencion estricta`, `--chunking fijo`, `--k N`, `--modelo haiku|sonnet|opus`, `--effort low|medium|high`, `--ejemplos`, `--razonar si|no`. El checkpoint `step-06` ya los trae; si trabajás con tu versión, pedile a Claude Code solo el flag de tu tarjeta.

## Criterios de terminado

- [ ] Corriste la eval base y leíste qué tipos de pregunta fallaron.
- [ ] Corriste tu variante y comparaste el puntaje contra la base.
- [ ] Marcaste los hitos `eval_base` y `eval_variante`.
- [ ] Podés explicar en una frase qué cambió y por qué (para la demo por pareja).

## Fuera de alcance

- Cambiar el banco de preguntas o el juez para mejorar el puntaje.
- Optimizar varias palancas a la vez: una por persona, para poder atribuir el efecto.
