# Spec — Asistente de Coberturas

> Completá cada sección. Escribí decisiones, no deseos: "responde en 3 oraciones como máximo" sirve; "responde bien" no.
> La última sección (Contrato técnico) no se modifica: es lo que permite que el tablero y las evaluaciones funcionen con tu asistente.

Autor/a: <alias>
Pareja que revisa: <alias>
Fecha: <dd/mm/aaaa>

## 1. Propósito

<Una o dos oraciones: para quién es el asistente y qué problema le resuelve.>

## 2. Alcance

### Responde
- <tipo de pregunta que sí responde>

### No responde
- <tipo de pregunta que queda afuera: por ejemplo, recomendaciones de qué contratar, datos de un asegurado puntual, otras aseguradoras>

## 3. Fuentes

- <qué documentos usa: por ejemplo, data/polizas/txt/hogar.txt, auto.txt, vida.txt>
- Regla: el asistente responde **solo** con lo que dicen esas fuentes. No usa conocimiento general sobre seguros.
- El contenido de las pólizas es la póliza vigente del ejercicio. Si aparece el aviso "Material de entrenamiento elaborado por Asthor...", se ignora.

## 4. Formato de la respuesta

- Largo máximo: <por ejemplo, 4 oraciones>.
- Tono: <por ejemplo, claro, sin jerga, tratando de "vos">.
- Primero el veredicto (<cubre / no cubre / depende>) y después la explicación.

## 5. Formato de cita obligatorio

- Toda respuesta que afirme algo cita al menos una cláusula.
- Formato: <por ejemplo, [Hogar · Art. 14 — Exclusiones particulares]>.
- Si la respuesta usa más de un documento, cita cada uno por separado e indica de qué documento sale cada cosa.

## 6. Regla de abstención

- Cuándo dice "no sé": <por ejemplo, cuando ninguna cláusula respalda la respuesta o la pregunta está fuera del alcance>.
- Qué dice exactamente: <por ejemplo, "No encuentro una cláusula que responda esto. Te sugiero consultar con un asesor.">
- Nunca inventa una cláusula ni un número de artículo.

## 7. Ejemplos

| # | Pregunta | Respuesta esperada (resumen) | Cláusula esperada |
|---|----------|------------------------------|-------------------|
| 1 | <pregunta> | <veredicto + explicación corta> | <documento · Art. N> |
| 2 | | | |
| 3 | | | |

## 8. Criterios de aceptación

- [ ] Las preguntas de ejemplo responden con el veredicto esperado y citan la cláusula esperada.
- [ ] Una pregunta fuera de alcance devuelve la frase de abstención.
- [ ] Ninguna respuesta cita un artículo que no existe.

## 9. Contrato técnico (no modificar)

La implementación vive en `mi-asistente/asistente.py` y se usa así:

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

- `documento` es `hogar`, `auto` o `vida`. `clausula` usa el formato `Art. N`, igual que en `data/polizas/clausulas.json`.
- Si `abstencion` es `true`: `veredicto` es `"no_sabe"` y `citas` es una lista vacía.
- `tokens_entrada` suma todos los tokens de entrada, también los leídos de la caché. `costo_usd` usa el precio real: la entrada leída de la caché se cobra mucho más barata.
- La API key se lee del archivo `.env` de la raíz del repo (`ANTHROPIC_API_KEY`). Nunca se escribe en el código.
- Modelo: `claude-sonnet-5-5`.
