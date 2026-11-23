# mi-asistente — tu carpeta de trabajo

Acá vive **tu** Asistente de Coberturas. Claude Code lo genera a partir de tu spec (`specs/asistente.md`) en el step 03 y lo vas mejorando en los pasos siguientes.

Lo que tiene que haber, como mínimo:

```
mi-asistente/
  asistente.py              la CLI (step 03)
  tests/test_guardrails.py  los Behavior Guardrails (step 04)
```

Se usa siempre igual (es el contrato técnico de la spec):

```
python mi-asistente/asistente.py "pregunta"
python mi-asistente/asistente.py --json "pregunta"
```

El tablero, los guardrails y las evaluaciones llaman a tu asistente por ese contrato. Si cambiás el nombre del archivo o el formato del JSON, dejan de funcionar.

## Si te atrasás

```
python tools/saltar.py step-03
```

Mueve tu trabajo de esta carpeta a `mi-asistente.backup-<hora>/` y copia acá la versión del checkpoint. No se pierde nada.

## No va en esta carpeta

- La API key (va en `.env`, en la raíz del repo).
- Datos de asegurados o de clientes, en ningún caso.
