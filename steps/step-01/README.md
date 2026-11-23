# Step 01 — Cómo funciona un LLM (v0)

**Bloque:** 13:20–14:00 del día 1.

## Qué vas a hacer

Correr cuatro scripts que le hacen a Claude la misma pregunta sobre la póliza de hogar, cambiando una cosa por vez: sin póliza, con póliza, con razonamiento. Cada uno imprime la respuesta, los tokens de entrada y salida, el costo en USD y el tiempo. El modelo está fijo (`claude-sonnet-5-5`) para que todos veamos los mismos números.

Spec del paso: [`specs/step-01.md`](../../specs/step-01.md).

## Comandos

Con el entorno activado, desde la raíz del repo:

```
python steps/step-01/01_pregunta.py
python steps/step-01/02_con_poliza.py
python steps/step-01/02_con_poliza.py --con-footer
python steps/step-01/03_razonamiento.py bajo
python steps/step-01/03_razonamiento.py alto
```

`04_modelos.py` (Haiku, Sonnet y Opus lado a lado) lo corre el instructor en pantalla.

Todos aceptan otra pregunta entre comillas, por ejemplo `python steps/step-01/02_con_poliza.py "¿Cubre el robo de una bicicleta?"`.

## Qué mirar

- **01 vs 02**: ¿la respuesta sin póliza cita un artículo? ¿Existe ese artículo? Compará con la respuesta de 02, que sí tiene la póliza. El modelo predice lo probable, no busca lo verdadero.
- **Tokens de entrada**: ¿cuánto sube cuando va la póliza? ¿Cuánto cuesta cada pregunta? Multiplicalo por mil consultas por día.
- **`--con-footer`**: la misma póliza, pero con el aviso "Material de entrenamiento..." en cada página. ¿Cambia la respuesta? Todo lo que entra al contexto influye.
- **bajo vs alto**: tokens de salida, tiempo y costo. ¿Mejoró la respuesta lo suficiente como para pagar la diferencia? Lo que se imprime como razonamiento es un resumen.

## Para discutir con tu pareja

1. ¿Por qué el modelo responde con seguridad aunque no tenga la póliza?
2. ¿Qué cuesta más: los tokens de entrada o los de salida? ¿Dónde se va la plata en este caso?
3. ¿Cuándo vale la pena el razonamiento alto en atención al cliente?

## Marcar el hito

Después de correr `02_con_poliza.py`:

```
python .claude/skills/marcar-avance/marcar.py step_01
```

(o pedile a Claude Code: "marcá el hito step_01").

## Si te atrasás

Corré al menos `01_pregunta.py` y `02_con_poliza.py` y marcá el hito. El resto lo vemos en la pantalla.
