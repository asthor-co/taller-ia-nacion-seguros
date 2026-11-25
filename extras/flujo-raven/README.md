# Flujo Raven: un skill por fase para desarrollar con Claude Code

Este es el flujo de desarrollo que usamos en Asthor en el proyecto Raven, tal cual: un comando de Claude Code por fase. Es el mismo método que hicieron a mano en el taller (spec, plan revisado, implementación, verificación), empaquetado para usarlo todos los días.

No está activo en este repo: está en `extras/` para que lo instales en tu propio proyecto.

## El flujo

| Fase | Comando | Qué deja | En el taller |
|---|---|---|---|
| 1. Entender | `/understand` | Un resumen del pedido, qué specs y qué código toca, y las preguntas abiertas. No escribe nada. | La entrevista de `/escribir-spec` |
| 2. Spec | `/spec` | Specs permanentes (entidades, flujos, pantallas) y un registro de cambios. | Step 02 |
| 3. Plan | `/plan` | Un plan con criterios de aceptación, cada uno con su oráculo. Otro agente escribe los tests **antes** del código, y tienen que fallar. Termina con el prompt para implementar. | Step 03, en modo plan |
| 4. Implementar | `/implement` | El código, en una **conversación nueva**, hasta que los tests pasan. No puede tocar los tests; un verificador independiente da el veredicto. | Step 03, guardrails (04) y evals (06) |
| 5. Commit | `/commit` | Un commit local, con el mensaje aprobado por vos. No pushea. | — |
| 6. Cerrar | `/close` | Cierra el issue y borra el plan y el registro de cambios: quedan las specs y el código. | — |
| Atajo | `/fix` | Para cambios chicos que no tocan specs: propone, espera tu OK, implementa. | — |

Tres ideas que lo sostienen:

1. **Cada fase deja un archivo que revisa una persona.** Ningún comando pasa solo a la fase siguiente.
2. **Contexto limpio para implementar.** `/plan` termina con un prompt listo para pegar en una conversación nueva: el plan tiene que alcanzar por sí solo.
3. **El que escribe el código no escribe los tests que lo juzgan.** Los criterios de aceptación se convierten en tests que fallan antes de implementar, los escribe otro agente, y el que implementa no los puede editar. Es la misma razón por la que en el taller el juez de las evals es otro modelo.

`commands/v2/` trae las referencias que usan `/plan` e `/implement`: los cuatro oráculos (`funcional`, `comportamiento`, `visual`, `humano`), cómo se escriben los tests en rojo y cómo se verifica. Nombran otras fases de la v2 (`/clarify`, `/build`, `/iterate`) que no están acá: es el loop autónomo, el que en Asthor corre como agentes.

## Instalarlo en tu proyecto

```bash
mkdir -p .claude/commands
cp -r extras/flujo-raven/commands/* .claude/commands/
```

En Claude Code aparecen como `/understand`, `/spec`, `/plan`, `/implement`, `/commit`, `/close` y `/fix`. Para usarlos en todos tus proyectos, copialos a `~/.claude/commands/`.

## Qué vas a tener que adaptar

Están escritos para el monorepo de Raven. Antes de usarlos en tu proyecto, ajustá:

- **Unidades:** suponen `apps/<unidad>/` y `packages/<unidad>/`, cada una con `PRODUCT.md`, `TECH.md`, `CLAUDE.md` y `specs/` (`entities/`, `flows/`, `ui/`, `plans/`). Si tu proyecto es uno solo, tratá la raíz como la única unidad.
- **Mockups:** `/plan` e `/implement` leen las pantallas desde Pencil (`.pen`) y usan el design system `@raven/ui`. Si no hay interfaz, esas partes no aplican.
- **Tests:** el entorno de prueba (`scripts/test-env.sh`, `TESTING.md`, `pnpm`) es el de Raven. Cambialo por cómo corrés los tests vos (por ejemplo, `pytest`).
- **Issues:** usan `gh` para leer y cerrar issues de GitHub. Si no usás issues, se saltea.

## Alternativa pública: Superpowers

[Superpowers](https://github.com/obra/superpowers), de Jesse Vincent y Prime Radiant, es una metodología abierta construida con skills, con la misma idea: el agente busca el skill que corresponde antes de cada tarea. Su flujo básico es parecido al de Raven:

1. `brainstorming`: saca qué querés y por qué, y te lo devuelve para corregir.
2. `using-git-worktrees`: una rama aislada con los tests en verde antes de empezar.
3. `writing-plans`: tareas de 2 a 5 minutos, con archivos exactos y cómo verificarlas.
4. `subagent-driven-development` o `executing-plans`: un subagente nuevo por tarea, con revisión después de cada una.
5. `test-driven-development`: test que falla, código mínimo, test que pasa.
6. `requesting-code-review`: revisión contra el plan; lo crítico frena.
7. `finishing-a-development-branch`: tests, y elegir entre merge, PR, dejarla o descartarla.

Es más genérico que el flujo Raven y no supone ninguna estructura de proyecto, así que es un buen punto de partida si no querés adaptar nada. Funciona con Claude Code, Codex, Cursor y otros agentes; las instrucciones de instalación están en su repositorio.
