---
name: marcar-avance
description: Verifica en la máquina del participante un hito del taller (entorno listo, step 01, spec, plan aprobado, primera cita, ejemplos, guardrails y los del día 2) y lo marca en el tablero proyectado. Usar cuando pidan "marcá mi avance", "marcá el hito ...", "actualizá el tablero" o "¿qué hitos me faltan?".
---

# Marcar avance en el tablero

El tablero es una planilla proyectada en la sala, con una fila por alias y una columna por hito. Este skill verifica el hito **en la máquina** (no alcanza con decir "ya lo hice") y lo envía. Nadie se loguea en Google desde la terminal.

## Cómo correrlo

Usá siempre el Python del entorno virtual del repo:

- Windows: `.venv/Scripts/python.exe`
- macOS: `.venv/bin/python`

(En los ejemplos de abajo dice `python`: reemplazalo por el de tu sistema si el entorno no está activado.)

```
python .claude/skills/marcar-avance/marcar.py <hito>        # verifica y envía un hito
python .claude/skills/marcar-avance/marcar.py --todos       # verifica y envía todos los que falten
python .claude/skills/marcar-avance/hitos.py --todos        # solo muestra el estado, no envía nada
python .claude/skills/marcar-avance/marcar.py --reenviar    # reenvía lo que quedó pendiente
python .claude/skills/marcar-avance/marcar.py --alias <alias>   # guarda el alias si falta
```

Si la persona no dice qué hito, preguntá cuál o corré `hitos.py --todos` para mostrarle el estado. `marcar.py --todos` llama varias veces a la API (cuesta unos centavos y tarda unos minutos): usalo solo si lo pide.

## Hitos

| Hito | Qué se verifica |
|------|-----------------|
| `entorno_listo` | `check_setup.py` pasó sin FALLAS (existe `.taller/setup_ok`) |
| `step_01` | se corrió `steps/step-01/02_con_poliza.py` (existe su salida en `.taller/`) |
| `spec` | `specs/asistente.md` tiene todas las secciones de la plantilla, sin textos `<...>` pendientes, y el contrato técnico intacto |
| `plan_aprobado` | `specs/plan.md` tiene la línea `Aprobado por: <alias de la pareja>` |
| `primera_cita` | el asistente responde una pregunta de ejemplo con una cita a una cláusula que existe |
| `ejemplos_ok` | las 5 preguntas de `data/preguntas_ejemplo.json` responden citando la cláusula correcta |
| `guardrails` | cuántos de los 3 guardrails pasan (`pytest mi-asistente/tests`); se envía el número, de 0 a 3 |
| `step_05` | hay un índice de Chroma y una respuesta trae documento y cláusula |
| `eval_base` | hay un resultado de `evaluar.py` sin variante en `resultados/` |
| `eval_variante` | hay un resultado de `evaluar.py` con `--variante` |
| `step_07` | las preguntas de `data/banco_seguridad.json` responden con el veredicto esperado |

Los hitos que prueban el asistente lo llaman por su contrato: `python mi-asistente/asistente.py --json "pregunta"`. Si el participante trabaja en otra ruta, definí `ASISTENTE_CMD` (por ejemplo `ASISTENTE_CMD="python checkpoints/step-04/asistente.py"`).

## Qué hacer con el resultado

- `[OK]` y "Enviado al tablero": listo. Decile que ya aparece en la pantalla.
- `[OK]` y "Quedó en .taller/pendientes.jsonl": el hito está verificado pero no se pudo mandar (sin `TABLERO_URL`, sin red o token incorrecto). Se reenvía solo la próxima vez que corra `marcar.py`. Si falta `TABLERO_URL` o `TABLERO_TOKEN`, pedile que los copie de la pantalla del instructor a `.env`.
- `[PENDIENTE]`: el hito no se cumple todavía. Explicale en una o dos frases qué falta, usando el detalle que imprime el script, y ofrecé ayudar. No marques nada a mano ni edites los archivos de `.taller/` para forzar un hito.

## Reglas

- Nunca muestres el contenido de `.env` ni el token. El script ya los oculta en lo que imprime.
- No modifiques `hitos.py` ni `marcar.py` para que un hito pase. Si un hito falla, se arregla el trabajo, no la verificación.
- Para `ejemplos_ok` o `guardrails` que fallan: la consigna del taller es corregir la spec y regenerar, no parchear el código a mano.
