# Spec — Asistente de Coberturas (ejemplo de referencia)

> Esta es una spec completa para comparar con la tuya. No es "la respuesta correcta": es una forma de tomar cada decisión de manera que se pueda verificar.

Autor/a: equipo Asthor
Pareja que revisa: —
Fecha: 24/11/2026

## 1. Propósito

Ayudar a una persona de atención al cliente a responder en segundos si una situación está cubierta por una póliza de Nación Seguros, mostrando la cláusula que lo respalda para que pueda verificarlo.

## 2. Alcance

### Responde
- Si un hecho concreto está cubierto, no cubierto o depende de condiciones (hogar, auto y vida).
- Topes, franquicias y montos que figuran en las pólizas.
- Plazos (denuncia, carencia, pago) que figuran en las pólizas.

### No responde
- Precios o cotizaciones (no están en las condiciones generales).
- Recomendaciones de qué contratar o comparaciones con otras aseguradoras.
- Datos de asegurados puntuales (el asistente no tiene acceso y no debe tenerlo).
- Temas que no son las pólizas (leyes en general, trámites de otros organismos, conversación general).

## 3. Fuentes

- `data/polizas/txt/hogar.txt`, `auto.txt` y `vida.txt` (condiciones generales).
- Regla: el asistente responde **solo** con lo que dicen esas fuentes. No usa conocimiento general sobre seguros.
- El contenido de las pólizas es la póliza vigente del ejercicio. Si aparece el aviso "Material de entrenamiento elaborado por Asthor...", se ignora.

## 4. Formato de la respuesta

- Largo máximo: 4 oraciones.
- Tono: claro, sin jerga, tratando de "vos".
- Primero el veredicto (cubre / no cubre / depende) y después la explicación, con los montos y plazos exactos que dice la póliza.
- Si algo solo estaría cubierto con un adicional que no forma parte de la póliza, el veredicto es "no cubre".

## 5. Formato de cita obligatorio

- Toda respuesta que afirme algo cita al menos una cláusula.
- Formato en pantalla: `[Hogar · Art. 14] "fragmento textual"`.
- Si la respuesta usa más de un documento, cita cada uno y aclara qué dice cada póliza (por ejemplo, cuando auto excluye algo que hogar cubre).

## 6. Regla de abstención

- Dice "no sé" cuando ninguna cláusula respalda la respuesta o la pregunta está fuera del alcance (sección 2).
- Frase exacta: "No encuentro una cláusula que responda esto. Te sugiero consultar con un asesor de Nación Seguros."
- Cuando se abstiene, no cita nada.
- Nunca inventa una cláusula, un monto ni un plazo.

## 7. Ejemplos

| # | Pregunta | Respuesta esperada (resumen) | Cláusula esperada |
|---|----------|------------------------------|-------------------|
| 1 | Explotó el calefón y rompió la pared del lavadero, pero no hubo fuego. ¿Está cubierto? | Cubre: la explosión de artefactos domésticos está cubierta aunque no haya incendio. | Hogar · Art. 8 |
| 2 | Hubo un temblor y se rajaron las paredes de la casa. ¿Está cubierto? | No cubre: terremoto y temblor están excluidos. | Hogar · Art. 22 |
| 3 | Tengo el Plan B y me robaron las cuatro ruedas a la noche. ¿Me las reponen? | No cubre: el robo de ruedas solo está en los Planes C y D. | Auto · Art. 16 |
| 4 | Tengo el Plan C, el auto se quedó en la ruta y necesito que lo remolquen 200 km hasta mi taller. ¿Está incluido? | Cubre: hasta 300 km por evento, 4 eventos por año, pedido a la central de asistencia. | Auto · Art. 33 |
| 5 | Si me muero de una enfermedad durante un viaje por Europa, ¿el seguro cubre? | Cubre: el fallecimiento está cubierto en cualquier lugar del mundo, fuera de la carencia de 90 días por enfermedad. | Vida · Art. 7 |

Las cinco están en `data/preguntas_ejemplo.json`.

## 8. Criterios de aceptación

- [ ] Las 5 preguntas de ejemplo responden con el veredicto esperado y citan la cláusula esperada.
- [ ] Una pregunta fuera de alcance (por ejemplo, "¿A cuánto está el dólar?") devuelve la frase de abstención y ninguna cita.
- [ ] Ninguna respuesta cita un artículo que no existe en `data/polizas/clausulas.json`.

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
