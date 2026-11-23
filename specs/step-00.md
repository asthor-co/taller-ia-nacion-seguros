# Spec — Step 00 (opcional): un agente mínimo

## Objetivo

Ver qué es un harness: un programa que llama a Claude por API, le ofrece herramientas y repite un loop hasta que el modelo deja de pedirlas y responde. Es, en chiquito, lo mismo que hacen Claude Code o un agente de voz.

## Entradas

- Una pregunta en lenguaje natural (opcional; hay una por defecto).
- Las pólizas en texto: `data/polizas/txt/hogar.txt`, `auto.txt`, `vida.txt`.
- La API key en `.env`.

## Salidas

- En la terminal, una línea por cada vuelta del loop: qué herramienta pidió el modelo y con qué argumentos (`[vuelta 1] herramienta=buscar_clausula args={...}`).
- La respuesta final del modelo.

## Cómo funciona

- Modelo fijo: `claude-sonnet-5-5`.
- Dos herramientas: `leer_poliza(nombre)` devuelve la póliza completa; `buscar_clausula(nombre, palabra)` devuelve los artículos que mencionan esa palabra.
- Loop: mientras el modelo pida herramientas, el programa las ejecuta y le devuelve el resultado. Corta a las 10 vueltas como máximo.
- El código ya está escrito (`steps/step-00/agente.py`, unas 70 líneas): se lee y se corre, no se escribe.

## Criterios de terminado

- [ ] `python steps/step-00/agente.py` corre y muestra al menos una vuelta con una herramienta y la respuesta final.
- [ ] Corriste una pregunta propia y podés explicar qué herramientas eligió el modelo y por qué.
- [ ] Podés señalar en el código las tres partes: modelo, herramientas y loop.

## Fuera de alcance

- Escribir o modificar el agente.
- Frameworks de agentes (Claude Agent SDK, Strands): se muestran en las slides.
- Citas con formato, abstención o cualquier regla de negocio: eso es el asistente, desde el step 02.
