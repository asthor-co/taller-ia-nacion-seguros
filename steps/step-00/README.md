# Step 00 (opcional) — Un agente mínimo

**Bloque:** 14:00–14:30 del día 1. Si falta tiempo, es el primer bloque que se recorta: ninguno de los pasos siguientes depende de este.

## Qué vas a hacer

Leer y correr `agente.py`: unas 70 líneas que muestran qué hay adentro de un agente. Un **harness** es el programa que rodea al modelo: le ofrece herramientas, ejecuta las que pide y le devuelve el resultado, una y otra vez, hasta que el modelo responde. Claude Code, que vas a usar el resto de la tarde, es un harness. Un agente de voz también.

Spec del paso: [`specs/step-00.md`](../../specs/step-00.md).

## Comandos

Con el entorno activado, desde la raíz del repo:

```
python steps/step-00/agente.py
python steps/step-00/agente.py "¿La póliza de hogar cubre la rotura de un vidrio?"
```

## Qué mirar

- Cada línea `[vuelta N] herramienta=... args=...` es una vuelta del loop: el modelo pidió una herramienta y el programa la ejecutó.
- ¿Qué herramienta eligió primero: `leer_poliza` (toda la póliza) o `buscar_clausula` (solo los artículos con una palabra)? ¿Con qué palabra buscó?
- Abrí `agente.py` y buscá las tres partes: el **modelo** (`MODELO`), las **herramientas** (`HERRAMIENTAS` y `ejecutar`) y el **loop** (`for vuelta in range(...)`).
- El modelo no ejecuta nada: solo pide. Quien ejecuta es el programa.

## Para discutir con tu pareja

1. ¿Qué pasaría si `buscar_clausula` devolviera artículos equivocados? ¿El modelo se daría cuenta?
2. ¿Por qué el loop corta a las 10 vueltas?
3. Cuando Claude Code te pide permiso para correr un comando, ¿en qué parte de este loop está?

## Si te atrasás

Saltealo: no hay hito para este paso y nada depende de él.
