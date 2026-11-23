# Step 05 — Prompts sugeridos

Primero el plan (modo plan, Shift+Tab), tu pareja lo revisa, después la implementación. Si una respuesta falla, corregí la spec, no el código.

## Prompt 1 — Plan del índice (modo plan)

```
Quiero que mi asistente deje de mandar las tres pólizas completas y use solo las cláusulas relevantes (RAG).
Proponé solo el plan, sin escribir código, para:

1. mi-asistente/indexar.py, que:
   - parte data/polizas/txt/hogar.txt, auto.txt y vida.txt POR CLÁUSULA: un pedazo por cada
     encabezado "Art. N — Título", sin mezclar dos artículos en un pedazo;
   - con --chunking fijo, como alternativa para comparar, corta cada 800 caracteres;
   - calcula embeddings con sentence-transformers y el modelo intfloat/multilingual-e5-small,
     anteponiendo "passage: " a cada pedazo y con normalize_embeddings=True;
   - carga el modelo primero con local_files_only=True (ya está descargado);
   - guarda todo en Chroma persistente en .chroma/ en la raíz del repo, una colección por tipo de chunking,
     con distancia coseno y metadatos documento y clausula;
   - apaga la telemetría de Chroma (ANONYMIZED_TELEMETRY=False y Settings(anonymized_telemetry=False)).
2. El cambio en mi-asistente/asistente.py:
   - calcula el embedding de la pregunta anteponiendo "query: ";
   - recupera las k cláusulas más cercanas (k=5 por defecto, flag --k N);
   - pasa al modelo solo esas cláusulas, cada una marcada con su documento y artículo;
   - mantiene el contrato técnico sin cambios.

No uses el modelo de embeddings por defecto de Chroma. No instales librerías nuevas.
```

Tu pareja revisa: ¿parte por cláusula de verdad? ¿Usa los prefijos `query: ` y `passage: `? (sin ellos, el modelo e5 recupera peor sin avisar). ¿El contrato queda igual?

## Prompt 2 — Implementar y probar

```
Implementá el plan. Después:
1. Corré python mi-asistente/indexar.py y decime cuántos pedazos quedaron por documento.
2. Corré la pregunta "Me rompieron la ventanilla del auto, que estaba cerrado con llave, y se llevaron la notebook que había dejado en el asiento. ¿Me cubre algún seguro?"
   y mostrame qué fragmentos se recuperaron y la respuesta.
3. Corré python -m pytest mi-asistente/tests -v.
```

## Prompt 3 — Si cita un solo documento cuando hacen falta dos

Primero la spec:

```
En la pregunta de la notebook el asistente citó solo <documento>. Mi spec dice que cuando usa más de un
documento tiene que citar cada uno. ¿El problema es que no se recuperó la cláusula del otro documento
(recuperación) o que el modelo la tenía y no la usó (spec y prompt)? Mostrame los fragmentos recuperados.
```

## Prompt 4 — Comparar

```
Corré python steps/step-05/comparar.py y explicame la tabla en tres líneas: tokens, costo y citas correctas.
```
