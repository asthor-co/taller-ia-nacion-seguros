# Spec — Step 02: la spec del asistente

## Objetivo

Escribir la spec de tu Asistente de Coberturas: qué responde y qué no, con qué fuentes, con qué formato de cita y qué dice cuando no sabe. Una spec es un conjunto de decisiones verificables, no un prompt suelto.

## Entradas

- La plantilla: `specs/plantilla-asistente.md` (la misma que usa el skill: `.claude/skills/escribir-spec/plantilla.md`).
- Las pólizas en texto (`data/polizas/txt/`) y el índice de cláusulas (`data/polizas/clausulas.json`).
- Material de contexto propio, **solo público o anonimizado**. Nunca datos de asegurados.
- El skill `escribir-spec`, que te entrevista.

## Salidas

- `specs/asistente.md` con las 9 secciones de la plantilla completas: propósito, alcance (sí / no), fuentes, formato de respuesta, formato de cita obligatorio, regla de abstención, de 3 a 5 ejemplos con respuesta y cláusula esperadas, criterios de aceptación y el contrato técnico.
- La sección "Contrato técnico (no modificar)" idéntica a la de la plantilla.

## Criterios de terminado

- [ ] `specs/asistente.md` existe, sin textos `<...>` pendientes.
- [ ] Tu pareja la revisó con `.claude/skills/escribir-spec/checklist.md` y los 8 ítems están tildados.
- [ ] La comparaste con `specs/ejemplo-asistente.md` y anotaste al menos una diferencia de criterio.
- [ ] Marcaste el hito `spec`.

## Fuera de alcance

- Escribir código (eso es el step 03).
- Cambiar el contrato técnico.
- Usar datos reales de clientes o asegurados.
