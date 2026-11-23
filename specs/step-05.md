# Spec — Step 05: RAG y citas verificables (v3)

## Objetivo

Dejar de mandar las tres pólizas completas en cada pregunta. El asistente parte las pólizas en cláusulas, las indexa en una base vectorial local y le pasa al modelo solo las más cercanas a la pregunta. Así el asistente puede crecer a cientos de pólizas, que no entran enteras en el contexto. Con tres pólizas y caché no hay ahorro: `comparar.py` muestra qué se gana y qué se pierde.

## Entradas

- Tu asistente v2 (el de ayer) en `mi-asistente/`, o el checkpoint: `python tools/saltar.py step-04`.
- Las pólizas en texto: `data/polizas/txt/hogar.txt`, `auto.txt`, `vida.txt`.
- El modelo de embeddings `intfloat/multilingual-e5-small` (ya descargado en el setup).
- Los prompts sugeridos: `steps/step-05/prompts.md`.

## Salidas

- `mi-asistente/indexar.py`:
  - Parte cada póliza **por cláusula** (un pedazo por `Art. N`, sin mezclar artículos). Como alternativa para comparar, `--chunking fijo` corta cada 800 caracteres.
  - Calcula los embeddings con `multilingual-e5-small` vía `sentence-transformers`, con el prefijo `passage: ` en cada cláusula.
  - Guarda los vectores en Chroma persistente en `.chroma/` (raíz del repo), con metadatos `documento` y `clausula`. Telemetría apagada (`ANONYMIZED_TELEMETRY=False`).
- `mi-asistente/asistente.py`:
  - Calcula el embedding de la pregunta con el prefijo `query: `.
  - Recupera las k cláusulas más cercanas (k=5 por defecto, `--k N` para cambiarlo) y pasa al modelo solo esas, cada una marcada con su documento y artículo.
  - Mantiene el contrato técnico sin cambios.

## Criterios de terminado

- [ ] `python mi-asistente/indexar.py` crea el índice sin errores.
- [ ] Los guardrails del día 1 siguen pasando: `pytest mi-asistente/tests -v`.
- [ ] La pregunta de la notebook robada dentro del auto se responde citando **los dos documentos** (auto y hogar) y diciendo qué dice cada uno.
- [ ] `python steps/step-05/comparar.py` muestra tokens, costo y % de citas correctas, día 1 contra RAG.
- [ ] Marcaste el hito `step_05`.

## Fuera de alcance

- Servidores de bases vectoriales o servicios en la nube: Chroma corre local, sin servidor.
- El modelo de embeddings por defecto de Chroma (entrenado casi solo en inglés).
- Evaluación con el banco completo (step 06).
