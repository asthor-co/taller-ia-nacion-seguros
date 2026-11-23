# Taller IA — Nación Seguros

Taller práctico de 8 horas (martes 24 y miércoles 25 de noviembre de 2026, de 13 a 17 h), dictado por Asthor.

Cada participante construye en su propia notebook un **Asistente de Coberturas**: una herramienta que responde qué cubre y qué no cubre una póliza, **citando la cláusula** que lo respalda, o dice "no sé" cuando ninguna cláusula lo respalda. Lo construimos con Claude Code, a partir de una spec escrita por vos. Se trabaja en parejas: cada uno construye el suyo y la pareja revisa la spec y el plan.

> Las pólizas de `data/polizas/` son **material ficticio de entrenamiento** elaborado por Asthor. No son pólizas vigentes de Nación Seguros. En el taller nunca se usan datos de asegurados.

## Qué vamos a hacer

| Momento | Qué tiene la aplicación |
|---------|-------------------------|
| v0 | Una pregunta suelta a Claude, con la póliza entera en el contexto. Sin citas confiables. |
| v1 | La CLI del asistente, construida desde tu spec: responde con la cláusula o dice "no sé". |
| v2 | Behavior Guardrails: el formato de la cita y la abstención se verifican solos. |

El día 2 seguimos desde v2 con búsqueda de cláusulas, evaluación con un banco de preguntas, seguridad y un canal de voz. El material del día 2 llega con la rama `dia-2`.

## Instalación

IT deja instalados en tu notebook Git, Python (3.11 a 3.13; recomendado 3.12) y Claude Code (ver [`docs/setup.md`](docs/setup.md)). Después:

1. Abrí una terminal en la carpeta del repo del taller y corré `claude`.
2. Pedile a Claude Code: **"preparame el entorno del taller"**.

El skill `setup-taller` crea el entorno virtual, instala las librerías, baja el modelo de embeddings, te pide el alias, la API key y los datos del tablero, arma el `.env` y corre el chequeo. Al final te muestra un resumen con OK o PENDIENTE por ítem.

Para chequear a mano en cualquier momento (con el entorno activado):

```
python check_setup.py
```

Cómo activar el entorno en tu terminal:

| Sistema | Comando |
|---------|---------|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| macOS | `source .venv/bin/activate` |

La API key vive **solo** en el archivo `.env` (que git ignora). No la pegues en el código ni la exportes en la terminal.

## Mapa del repo

```
README.md               este archivo
check_setup.py          chequeo del entorno (OK / PENDIENTE / FALLA)
requirements.txt        librerías de Python, con versiones fijadas
.env.example            modelo del .env (la key va en .env, nunca en el repo)
docs/setup.md           guía de instalación y problemas frecuentes
.claude/
  settings.json         permisos para que Claude Code no pregunte por cada comando de Python
  skills/
    setup-taller/       "preparame el entorno del taller"
    escribir-spec/      entrevista para escribir tu spec (plantilla y checklist)
    marcar-avance/      verifica tus hitos y los marca en el tablero
data/
  polizas/pdf/          pólizas de hogar, auto y vida en PDF
  polizas/txt/          las mismas pólizas en texto (sin el pie de página)
  polizas/clausulas.json  índice de cláusulas: documento, artículo, título y texto
  preguntas_ejemplo.json  5 preguntas con su respuesta y cláusula esperadas
  preguntas_fuera_de_poliza.json  preguntas que el asistente no debe responder
specs/
  step-00.md ... step-04.md   qué se hace en cada paso
  plantilla-asistente.md      plantilla de la spec del asistente
  ejemplo-asistente.md        una spec completa para comparar con la tuya
steps/
  step-00/              agente mínimo: modelo + herramientas + loop (opcional)
  step-01/              cómo funciona un LLM: tokens, costo, contexto, razonamiento
  step-02/              la spec del asistente
  step-03/              construcción con Claude Code (prompts sugeridos)
  step-04/              Behavior Guardrails (prompts sugeridos)
checkpoints/
  step-02/ ... step-04/ una versión que funciona al final de cada paso
mi-asistente/           TU carpeta de trabajo: acá vive tu asistente
tools/
  pdf_a_texto.py        convierte los PDF a texto
  clausulas.py          regenera el índice de cláusulas
  saltar.py             salta a un checkpoint (con backup de tu trabajo)
```

## El contrato de la CLI

Todo asistente del taller, el tuyo incluido, se usa igual. Así el tablero y las verificaciones funcionan con cualquier implementación:

```
python mi-asistente/asistente.py "pregunta"           → respuesta legible con la cita
python mi-asistente/asistente.py --json "pregunta"    → solo este JSON en la salida estándar
```

```json
{
  "respuesta": "texto de la respuesta",
  "veredicto": "cubre | no_cubre | depende | no_sabe",
  "citas": [{"documento": "hogar", "clausula": "Art. 14", "texto": "fragmento citado"}],
  "abstencion": false,
  "uso": {"modelo": "claude-sonnet-5-5", "tokens_entrada": 0, "tokens_salida": 0, "costo_usd": 0.0}
}
```

- `documento` es `hogar`, `auto` o `vida`; `clausula` usa el formato `Art. N`, igual que `data/polizas/clausulas.json`.
- Si `abstencion` es `true`: `veredicto` es `"no_sabe"` y `citas` es una lista vacía.
- La API key se lee de `.env`. El modelo es `claude-sonnet-5-5`, igual para todos.

Este contrato está en la última sección de la plantilla de spec, marcado "no modificar".

## Si te atrasás: checkpoints

Cada carpeta de `checkpoints/` tiene una versión que funciona **al final** de ese paso. Si te quedaste atrás, saltá:

```
python tools/saltar.py step-03
python tools/saltar.py --lista       # muestra los checkpoints disponibles
```

`saltar.py` primero mueve tu trabajo a `mi-asistente.backup-<hora>/` (no se pierde nada) y después copia el checkpoint en `mi-asistente/`. Con `step-02` deja la spec de ejemplo en `specs/asistente.md` (y respalda la tuya si ya tenías una).

## Hitos y tablero

En la sala se proyecta un tablero con una fila por alias y una columna por hito. Los hitos se verifican en tu máquina y se envían solos:

```
python .claude/skills/marcar-avance/marcar.py spec
```

O pedile a Claude Code: "marcá mi avance". Hitos del día 1: `entorno_listo`, `step_01`, `spec`, `plan_aprobado`, `primera_cita`, `ejemplos_ok`, `guardrails`. Si no hay conexión con el tablero, el envío queda guardado en `.taller/pendientes.jsonl` y se reenvía la próxima vez. Ver [`.claude/skills/marcar-avance/SKILL.md`](.claude/skills/marcar-avance/SKILL.md).

## Ramas

El repo crece a medida que avanza el taller:

| Rama | Cuándo aparece | Qué trae |
|------|----------------|----------|
| `dia-1` | antes del taller | steps 00 a 04, checkpoints 02 a 04 |
| `dia-2` | miércoles a la mañana | steps 05 a 07, checkpoints 05 a 07 y el banco de preguntas |
| `referencia` | al final del día 2 | una implementación completa para comparar |

Para pasar a la rama nueva cuando el instructor lo indique (tu trabajo en `mi-asistente/` se conserva):

```
git fetch
git checkout dia-2
```

Si git dice que tus cambios se pisarían, pedile ayuda a Claude Code o al instructor antes de forzar nada.

## Plan B y verificación automática (sin probar)

- `.devcontainer/devcontainer.json`: entorno en la nube (GitHub Codespaces) con Python 3.12 y Claude Code, por si una notebook no logra instalar. **Sin probar.**
- `.github/workflows/check.yml`: corre `check_setup.py --offline` en Windows, macOS y Linux con Python 3.11 y 3.12. **Sin probar.**
