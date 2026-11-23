# Checklist de revisión de la spec (para tu pareja)

Leé `specs/asistente.md` de tu pareja y marcá cada ítem. Si alguno no se cumple, anotá qué falta y que lo corrija antes de pasar al plan.

- [ ] **1. Propósito concreto.** Dice para quién es el asistente y qué problema le resuelve, en una o dos oraciones.
- [ ] **2. Alcance con los dos lados.** Hay al menos dos tipos de pregunta que responde y al menos tres que no responde (por ejemplo: precios, recomendaciones de qué contratar, datos de un asegurado).
- [ ] **3. Fuentes acotadas.** Lista los documentos que usa y dice que responde solo con esas fuentes, sin conocimiento general.
- [ ] **4. Formato de cita verificable.** Hay un formato de cita con un ejemplo concreto (documento + artículo + fragmento), y dice qué hacer cuando la respuesta usa más de una póliza.
- [ ] **5. Abstención con frase exacta.** Dice cuándo responde "no sé", cuál es la frase literal, y que en ese caso no cita nada.
- [ ] **6. Nada inventado.** Dice explícitamente que nunca inventa una cláusula, un monto ni un plazo.
- [ ] **7. Ejemplos que existen.** Hay de 3 a 5 preguntas de ejemplo con veredicto y cláusula esperada, y abriste `data/polizas/txt/` para confirmar que al menos dos de esas cláusulas existen y dicen eso. Al menos un ejemplo es de algo que **no** está cubierto.
- [ ] **8. Contrato intacto y sin huecos.** No quedan textos entre `<...>` sin completar, y la sección "9. Contrato técnico (no modificar)" es idéntica a la de la plantilla.

Cuando los 8 estén tildados, tu pareja marca el hito: `python .claude/skills/marcar-avance/marcar.py spec`.
