# Step 06 — Evaluación (v4)

**Bloque:** 14:30–15:15 del día 2.

## Qué vas a hacer

Los guardrails verifican reglas; las evals miden calidad. Vas a correr tu asistente contra un banco común de 59 preguntas (con trampas: exclusiones escondidas, cláusulas ambiguas, preguntas que mezclan dos pólizas, fuera de póliza) y obtener un puntaje comparable entre todos. Después, cada integrante de la pareja prueba una palanca y mide su efecto.

Tres métricas:

| Métrica | Cómo se mide |
|---------|--------------|
| Acierto | Otro modelo (LLM como juez) compara tu respuesta contra la esperada. |
| Cita correcta | Sin modelo: alguna cláusula citada está entre las correctas. |
| Abstención correcta | En las preguntas fuera de póliza, dice que no sabe. |

Spec del paso: [`specs/step-06.md`](../../specs/step-06.md). Tarjetas: [`tarjetas.md`](tarjetas.md).

## Pasos

1. **14:30–14:40 — Instructor**: el banco, las métricas y el juez.
2. **14:40–14:50 — Puntaje base**:

   ```
   python steps/step-06/evaluar.py --rapido
   ```

   Evalúa 20 preguntas del banco, siempre las mismas, elegidas por tipo: tarda menos de un minuto. Al final muestra una tabla por tipo de pregunta y la lista de las que fallaron, con el motivo.
3. **14:50–15:05 — Tu palanca.** Cada pareja recibe una tarjeta; cada integrante prueba una de las dos variantes:

   ```
   python steps/step-06/evaluar.py --rapido --variante "k=3" --args "--k 3"
   ```

   El `--variante` es el nombre de la corrida (aparece en `resultados/`); `--args` son los flags que se le pasan a tu asistente. Base y variante, siempre con `--rapido`: si las dos no corren las mismas preguntas, los puntajes no se pueden comparar.
4. **15:05–15:15 — Puesta en común**: cada pareja lee base, variante y diferencia. Miramos el efecto de las siete palancas.

Si te sobra tiempo, corré base y variante sin `--rapido`: el banco completo (59 preguntas) tarda unos 5 minutos por corrida y da un puntaje más estable.

## Las palancas y tu asistente

El checkpoint `step-06` ya acepta todos los flags de las tarjetas. Si seguís con tu propia versión, pedile a Claude Code **solo** el flag de tu tarjeta:

```
Agregá a mi-asistente/asistente.py el flag <flag de la tarjeta> que hace <lo que dice la tarjeta>,
sin cambiar el comportamiento por defecto ni el contrato técnico.
```

## Qué mirar

- ¿Qué tipo de pregunta falla más? ¿Es un problema de recuperación, de la spec o del modelo?
- Abrí `resultados/<tu-alias>-...json` y leé los motivos del juez en 2 o 3 preguntas falladas. ¿Estás de acuerdo con el juez?
- Tu variante: ¿cambió el puntaje más que la diferencia entre dos corridas iguales? Si no, no hay efecto que reportar.
- El costo de la corrida (al final de la salida). ¿Vale la mejora?

## Para discutir con tu pareja (y para la demo de las 15:50)

1. ¿Qué palanca probaste y cómo cambió el puntaje?
2. ¿Confiarías en un asistente sin un banco de preguntas como este?
3. ¿Qué preguntas tendría que tener el banco de tu área?

## Verificar los hitos

```
python .claude/skills/marcar-avance/hitos.py eval_base
python .claude/skills/marcar-avance/hitos.py eval_variante
```

## Si te atrasás

```
python tools/saltar.py step-06
python mi-asistente/indexar.py
python steps/step-06/evaluar.py --rapido
```
