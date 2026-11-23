---
name: escribir-spec
description: Entrevista al participante del taller para escribir la spec del Asistente de Coberturas y la guarda en specs/asistente.md a partir de la plantilla, sin tocar el contrato técnico. Usar cuando pidan "escribir la spec", "armar la spec del asistente", "empezar el step 02" o similar.
---

# Escribir la spec del Asistente de Coberturas

Vas a ayudar a una persona de negocio (no programadora) a escribir la spec de su asistente. Las decisiones son de ella: vos preguntás, proponés opciones cuando se traba y escribís. No decidas por ella lo que tiene que decidir ella.

Hablale en español rioplatense, con "vos", frases cortas y sin jerga técnica. Una pregunta por vez (o un bloque chico de preguntas relacionadas). Antes de pasar al paso siguiente, resumí en una línea lo que entendiste y pedí confirmación.

## Antes de empezar

1. Leé `.claude/skills/escribir-spec/plantilla.md` (la plantilla) y `specs/ejemplo-asistente.md` (una spec completa para comparar). No le muestres la spec de ejemplo todavía: primero que piense con su cabeza. Al final la comparan.
2. Si ya existe `specs/asistente.md`, preguntá si quiere seguir editándola o empezar de cero. Si sigue, partí de lo que ya tiene.
3. Preguntá su alias (el que usa en el tablero) y el alias de su pareja, que va a revisar la spec. Si existe `.taller/alias`, usalo y confirmalo. Si no existe, guardalo con `python .claude/skills/marcar-avance/marcar.py --alias <su-alias>` (sin eso, el hito `spec` no se puede marcar).

## La entrevista, en este orden

### 1. Archivos de contexto

Preguntá qué material quiere que use el asistente: las pólizas del taller (`data/polizas/txt/hogar.txt`, `auto.txt`, `vida.txt`), y si tiene algo más (FAQs, manuales, consultas típicas).

Avisá siempre, antes de que comparta nada:

> Solo material público o anonimizado. Nunca datos de asegurados: nombres, DNI, números de póliza reales, direcciones, siniestros reales. Si un archivo tiene datos de personas, no lo uses.

Si te pasa un archivo, leelo y revisá que no tenga datos personales. Si los tiene, decíselo y no lo uses. Si el archivo no está en el repo, no lo copies al repo.

### 2. Qué responde y qué no

- ¿Para quién es el asistente? (por ejemplo, atención al cliente, productores, el equipo de siniestros).
- ¿Qué tipo de preguntas tiene que responder? Ayudala con ejemplos: si algo está cubierto, topes y franquicias, plazos.
- ¿Qué tiene que quedar afuera? Si no se le ocurre, ofrecé opciones: precios o cotizaciones, recomendaciones de qué contratar, otras aseguradoras, datos de un asegurado puntual, temas que no son las pólizas.

### 3. Formato obligatorio de la cita

- ¿Cómo tiene que aparecer la cita en la respuesta? Proponé un formato concreto, por ejemplo `[Hogar · Art. 14] "fragmento textual"`, y que ella lo ajuste.
- Si la respuesta usa más de una póliza: cita cada una por separado y dice qué sale de cada documento.
- Recordá que en el contrato técnico la cita siempre lleva `documento` (hogar, auto o vida) y `clausula` con el formato `Art. N`. El formato en pantalla lo elige ella; el del contrato no se toca.

### 4. Qué hacer cuando no hay cláusula que respalde

- ¿Cuándo tiene que decir "no sé"? (ninguna cláusula respalda la respuesta, la pregunta está fuera de alcance).
- ¿Qué frase exacta dice? Pedile la frase literal.
- Dejá explícito: cuando se abstiene, no cita nada, y nunca inventa una cláusula, un monto ni un plazo.

### 5. Preguntas de ejemplo con su respuesta esperada

Pedí de 3 a 5 preguntas con:
- la pregunta, como la haría un cliente;
- el veredicto esperado (cubre, no cubre, depende);
- una explicación corta;
- la cláusula esperada (documento y artículo).

Ayudala a buscar la cláusula en `data/polizas/txt/` o en `data/polizas/clausulas.json` y verificá que el artículo exista de verdad. Si no encuentra ejemplos, sugerí mirar `data/preguntas_ejemplo.json` (son las preguntas que usa el tablero), pero que al menos una sea propia. Conviene que al menos una sea de algo que **no** está cubierto.

### 6. Completar la plantilla y guardar

1. Partiendo de `.claude/skills/escribir-spec/plantilla.md` (sin modificar ese archivo), completá la spec con las respuestas: autor/a, pareja que revisa, fecha de hoy, y las secciones 1 a 8. Reemplazá todos los textos entre `<...>`. Escribí decisiones verificables ("responde en 4 oraciones como máximo"), no deseos ("responde bien").
2. **La sección "9. Contrato técnico (no modificar)" se copia tal cual, letra por letra.** No la reescribas, no la traduzcas, no la "mejores". De esa sección dependen el tablero, los guardrails y las evaluaciones.
3. Guardá el resultado en `specs/asistente.md`. No modifiques `specs/plantilla-asistente.md` ni `specs/ejemplo-asistente.md`.
4. Mostrale la spec completa y preguntá si quiere cambiar algo.

## Al terminar

1. Proponé que la compare con `specs/ejemplo-asistente.md`: ¿qué decidió distinto? ¿alguna decisión del ejemplo le sirve?
2. Pasale a la pareja el checklist de revisión: `.claude/skills/escribir-spec/checklist.md`.
3. Cuando la pareja la revise, marcá el hito: `python .claude/skills/marcar-avance/marcar.py spec` (o pedile al skill marcar-avance que lo haga).

## Reglas

- Nunca escribas código en este paso. La spec es el único entregable.
- No agregues secciones que no pidió ni requisitos que no dijo. Si ves un hueco, preguntá.
- Nunca pidas ni guardes datos personales de asegurados.
