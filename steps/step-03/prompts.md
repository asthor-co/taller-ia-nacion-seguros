# Step 03 — Prompts sugeridos

Copiá y pegá en Claude Code. Lo que está entre `<...>` lo completás vos.

Regla del bloque: **si una respuesta falla, corregí la spec, no el código.** La spec es lo que vos decidís; el código es lo que Claude Code genera a partir de ella.

---

## Prompt 1 — Solo el plan (en modo plan)

Activá el modo plan (Shift+Tab hasta que abajo diga *plan mode*) y pegá:

```
Leé specs/asistente.md (mi spec), data/polizas/clausulas.json y data/preguntas_ejemplo.json.
Quiero implementar el Asistente de Coberturas en mi-asistente/asistente.py, cumpliendo mi spec
y la sección "Contrato técnico (no modificar)" al pie de la letra.

Proponé solo el plan, sin escribir código. Incluí:
1. Qué archivos vas a crear (solo dentro de mi-asistente/).
2. Cómo carga las pólizas de data/polizas/txt/ (hogar, auto y vida).
3. Cómo arma el prompt a partir de mi spec: alcance, formato de cita, regla de abstención.
4. Cómo garantiza que --json imprima solo el JSON del contrato, aunque el modelo se equivoque de formato.
5. Cómo se abstiene (veredicto no_sabe, abstencion true, citas vacía).
6. Cómo lo vamos a probar con las 5 preguntas de data/preguntas_ejemplo.json.

Restricciones: Python, solo las librerías de requirements.txt, la API key desde el .env de la raíz
con python-dotenv, modelo claude-sonnet-5-5. No modifiques data/, tools/ ni specs/asistente.md.
Las tres pólizas son iguales en cada pregunta: mandalas en un bloque aparte con prompt caching
(cache_control) y calculá el costo con el precio de lectura de caché.
Escribí el plan en español y para alguien que no programa.
```

## Revisión de la pareja (antes de aprobar)

Tu pareja lee el plan y responde:

- [ ] ¿Respeta el alcance de la spec (lo que responde y lo que no)?
- [ ] ¿Usa el formato de cita y la frase de abstención exactos de la spec?
- [ ] ¿Respeta el contrato técnico (mismos campos, `--json` imprime solo JSON)?
- [ ] ¿Agrega algo que nadie pidió (servidor, base de datos, interfaz web, librerías nuevas)? Si sí, que lo saque.
- [ ] ¿Dice cómo se va a probar?

Si algo no cierra, pedile a Claude Code que ajuste el plan antes de seguir.

## Prompt 2 — Guardar el plan aprobado

```
Guardá el plan aprobado en specs/plan.md, tal cual quedó, y agregá al final la línea:
Aprobado por: <alias de tu pareja>
```

Marcá el hito: `python .claude/skills/marcar-avance/marcar.py plan_aprobado`.

## Prompt 3 — Implementar (fuera del modo plan)

Salí del modo plan (Shift+Tab) y pegá:

```
Implementá el plan de specs/plan.md.
Cuando termines, corré cada pregunta de data/preguntas_ejemplo.json con
python mi-asistente/asistente.py --json "<pregunta>"
y mostrame una tabla con: id, veredicto, cláusulas citadas, cláusula esperada y si coinciden.
Después corré una pregunta fuera de alcance ("¿A cuánto está el dólar oficial hoy?") y mostrame el JSON.
No instales librerías nuevas. No modifiques data/, tools/ ni specs/asistente.md.
```

Apenas tengas una respuesta correcta con cita: `python .claude/skills/marcar-avance/marcar.py primera_cita`.

## Prompt 4 — Iterar sobre la spec, no sobre el código

Cuando una respuesta falla:

```
La pregunta "<pregunta>" respondió <lo que respondió> y esperaba <lo esperado> (cláusula <documento · Art. N>).
No toques el código todavía. Explicame qué parte de specs/asistente.md llevó a esa respuesta
y proponé un cambio en la spec que lo corrija. Mostrame el cambio antes de aplicarlo.
```

Cuando apruebes el cambio:

```
Aplicá el cambio en specs/asistente.md y regenerá la parte del asistente que depende de esa sección.
Volvé a correr las 5 preguntas de ejemplo y mostrame la tabla.
```

Cuando las 5 coinciden: `python .claude/skills/marcar-avance/marcar.py ejemplos_ok`.

## Prompt 5 — Entender lo que se generó

```
Explicame mi-asistente/asistente.py en 10 líneas, para alguien que no programa:
qué hace cada parte y en qué parte del código está cada regla de mi spec.
```
