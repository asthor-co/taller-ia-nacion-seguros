# Checklist de revisión del código generado

El código lo escribió Claude Code; la responsabilidad de lo que hace es tuya. Revisalo en pareja antes de mostrarlo o de usar algo parecido en tu área. Para cada ítem: OK, PROBLEMA (con archivo y línea) o NO APLICA. Podés pedirle a Claude Code que haga la primera pasada (prompt 5 de `prompts.md`), pero la decisión es de ustedes.

## Secretos

- [ ] **1. La key está en `.env` y `.env` está ignorado.** `git check-ignore .env` imprime `.env`, y `git status` no muestra el `.env` para subir.
- [ ] **2. No hay keys ni tokens en el código.** Buscá `sk-ant-`, `api_key=`, `TOKEN=` en `mi-asistente/`. La key se lee del entorno (cargado desde `.env`), nunca se escribe en un archivo `.py`.
- [ ] **3. No hay keys en logs ni en la salida.** Ningún `print` o log muestra la key, el token del tablero ni el contenido de `.env`, tampoco en mensajes de error.

## Datos

- [ ] **4. No hay datos personales en logs ni en archivos.** Las preguntas y respuestas que se guardan (caché, resultados, logs) no deberían tener nombres, DNI, números de póliza ni datos de salud. En producción, las preguntas de clientes son datos personales.
- [ ] **5. Las dependencias están fijadas.** Solo se usan las librerías de `requirements.txt`, con versión exacta (`==`). Nada instalado "a mano" que el código necesite.

## Robustez

- [ ] **6. Hay timeouts.** Las llamadas a la API y a otros procesos tienen un tiempo máximo; nada puede quedar colgado para siempre.
- [ ] **7. Los errores de la API se manejan.** Key inválida, sin conexión, límite de pedidos (429) o servicio sobrecargado (529) terminan con un mensaje claro y, donde corresponde, con reintentos con espera. Nunca con un traceback que muestre datos internos.

## Entradas no confiables

- [ ] **8. Todo lo que viene de afuera se trata como dato.** La pregunta del usuario, el texto de los PDF y cualquier respuesta de una herramienta son entradas no confiables: van marcadas como datos en el prompt (`<documento>...</documento>`) y nunca se concatenan como si fueran instrucciones del sistema.
- [ ] **9. Hay defensa contra inyección de instrucciones.** El system prompt dice que los documentos nunca son instrucciones, la ingesta descarta texto invisible y el guardrail `cita_respalda` verifica que la cita respalde la respuesta.
- [ ] **10. Nunca se ejecuta texto producido por el modelo.** No hay `eval`, `exec`, `subprocess` ni `os.system` con algo que haya generado el modelo, ni rutas de archivo que salgan de su respuesta. La salida del modelo se valida (JSON con esquema) antes de usarla.

## Permisos

- [ ] **11. Permisos mínimos.** El asistente solo lee `data/` y escribe en sus propias carpetas (`.chroma/`, `data/polizas/txt_limpio/`). La key es de un proyecto con límite de gasto. En `.claude/settings.json` no hay permisos más amplios que los necesarios (nada de `git push`, borrar carpetas o comandos de red).

## Hallazgos

| # | Ítem | Archivo y línea | Qué encontramos | Qué haríamos |
|---|------|-----------------|-----------------|--------------|
| 1 | | | | |
| 2 | | | | |
