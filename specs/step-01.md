# Spec — Step 01: primera pregunta (v0)

## Objetivo

Entender cómo responde un LLM y cuánto cuesta: qué pasa cuando le preguntás sin la póliza, qué cambia cuando se la das en el contexto, cómo se cuentan los tokens y qué agrega el razonamiento.

## Entradas

- La póliza de hogar en texto (`data/polizas/txt/hogar.txt`) y su versión con el pie de página (`hogar_con_footer.txt`).
- Una pregunta sobre una cobertura (hay una por defecto en los scripts).
- La API key en `.env`.

## Salidas

Cada script imprime la respuesta y las métricas: tokens de entrada, tokens de salida, costo en USD y tiempo.

| Script | Qué hace |
|--------|----------|
| `01_pregunta.py` | La pregunta sin la póliza. |
| `02_con_poliza.py` | La misma pregunta con la póliza en el contexto (`--con-footer` para la versión con el aviso del pie). Deja una copia de la respuesta en `.taller/step01_con_poliza.txt`. |
| `03_razonamiento.py bajo\|alto` | La misma pregunta y póliza con razonamiento; imprime primero el resumen del razonamiento y después la respuesta. |
| `04_modelos.py` | (demo del instructor) Haiku, Sonnet y Opus lado a lado: costo, tiempo y respuesta. |

`comun.py` tiene el cliente, la tabla de precios por modelo y la función que imprime las métricas. Modelo fijo: `claude-sonnet-5-5`, para que todas las mesas vean los mismos números.

## Criterios de terminado

- [ ] Corriste `01_pregunta.py` y `02_con_poliza.py` y comparaste tokens, costo y respuesta.
- [ ] Corriste `02_con_poliza.py --con-footer` y viste si cambia la respuesta.
- [ ] Corriste `03_razonamiento.py bajo` y `alto` y comparaste tokens, tiempo y costo.
- [ ] Marcaste el hito `step_01`.

## Fuera de alcance

- Escribir código: los scripts ya están.
- Citas verificables y abstención (step 02 en adelante).
- Varias pólizas a la vez.
