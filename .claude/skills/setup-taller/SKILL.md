---
name: setup-taller
description: Prepara la notebook del participante para el taller de IA de Nación Seguros: verifica Git y Python, clona o actualiza el repo, crea el entorno virtual, instala las librerías, descarga el modelo de embeddings, arma el .env con la API key sin mostrarla y corre check_setup.py. Usar cuando pidan "preparame el entorno del taller", "configurá el taller", "instalá lo del taller" o cuando check_setup.py falle.
---

# Preparar el entorno del taller

La persona que te pide esto no es programadora. Explicá cada paso en una frase, en español rioplatense y con "vos". Corré vos los comandos; pedile que haga algo solo cuando no se pueda evitar (instalar un programa con permisos, pegar la key). Si un paso falla, diagnosticá y proponé el arreglo antes de seguir.

Al final siempre imprimís un resumen con OK o PENDIENTE por ítem.

## 0. Detectá el sistema

Averiguá si es Windows o macOS y qué shell estás usando. Usá siempre rutas relativas al repo y comandos que funcionen en ese sistema. En Windows, con Git instalado, Claude Code usa Git Bash: ahí funcionan las barras `/`.

Python del entorno virtual (lo vas a usar en todos los pasos, en vez de activar el entorno):

- Windows: `.venv/Scripts/python.exe`
- macOS: `.venv/bin/python`

## 1. Git y Python 3.11+

Corré `git --version` y la versión de Python:

- Windows: `py -3.12 --version` (o `py -3.11`, `py -3.13`), y si no existe `py`, `python --version`.
- macOS: `python3.12 --version` (o `python3.11`, `python3.13`), y si no, `python3 --version`.

Se necesita Python 3.11, 3.12 o 3.13 (recomendado 3.12). El `python3` que trae macOS suele ser 3.9: no sirve.

Si falta algo, guiá la instalación (la hace la persona, puede pedir permisos de administrador; si no los tiene, que llame al contacto de IT):

| Falta | Windows | macOS |
|-------|---------|-------|
| Git | `winget install --id Git.Git -e`, o el instalador de https://git-scm.com/download/win | `xcode-select --install`, o `brew install git` |
| Python 3.12 | `winget install --id Python.Python.3.12 -e`, o el instalador de https://www.python.org/downloads/ (tildar "Add python.exe to PATH") | `brew install python@3.12`, o el instalador de https://www.python.org/downloads/ |

Después de instalar, hay que cerrar y volver a abrir la terminal (y Claude Code) para que aparezca en el PATH.

Node.js no hace falta para el taller (Claude Code se instala con el instalador nativo).

## 2. Clonar o actualizar el repo

- Si ya estás dentro del repo del taller (existe `check_setup.py` y `data/polizas/`): corré `git status`. Si no hay cambios propios, `git pull`. Si hay cambios, no los pises: avisá y seguí sin actualizar.
- Si no: pedile la URL del repo (la proyecta el instructor), clonalo con `git clone <url>` en una carpeta sin espacios ni acentos (por ejemplo `C:\taller` o `~/taller`) y trabajá desde ahí. Decile que abra Claude Code dentro de esa carpeta.

Nunca descargues el repo como zip: sin git no funcionan `saltar.py` ni la verificación del `.env`.

## 3. Entorno virtual e instalación de librerías

Desde la raíz del repo:

- Windows: `py -3.12 -m venv .venv` (o el Python que encontraste en el paso 1)
- macOS: `python3.12 -m venv .venv`

Si `.venv` ya existe y su Python es 3.11 a 3.13, reusalo.

Después, con el Python del entorno:

```
<python del entorno> -m pip install --upgrade pip
<python del entorno> -m pip install -r requirements.txt
```

La instalación baja unos 800 MB (torch incluido) y tarda varios minutos: avisalo. Corré el comando con un timeout largo (10 minutos).

Si falla:
- Error de SSL, de certificado o "connection" → es el proxy. Ver `docs/setup.md`, sección Proxy. Probá `<python del entorno> -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt` solo si la persona confirma que es una red corporativa con inspección de tráfico.
- "No matching distribution" → el Python no es 3.11 a 3.13. Volvé al paso 1.

Contale cómo activar el entorno en su propia terminal (para correr los scripts a mano):

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Windows cmd: `.venv\Scripts\activate.bat`
- Windows Git Bash: `source .venv/Scripts/activate`
- macOS: `source .venv/bin/activate`

Si PowerShell dice que la ejecución de scripts está deshabilitada, que use cmd o Git Bash. No cambies la política de ejecución.

## 4. Descargar el modelo de embeddings

El día 2 se usa `intfloat/multilingual-e5-small` (unos 470 MB). Bajalo ahora, con red:

```
<python del entorno> -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"
```

Si falla por red: el proxy tiene que permitir `huggingface.co` y sus dominios de descarga (`cdn-lfs.huggingface.co`, `*.hf.co`, `*.xethub.hf.co`). Ver `docs/setup.md`. Marcalo PENDIENTE y seguí.

## 5. Alias, API key y tablero

Pedí, de a uno:

1. **Alias**: el nombre con el que aparece en el tablero proyectado. Puede ser un apodo; no hace falta el nombre real. Sin espacios (si tiene, reemplazalos por guiones).
2. **API key de Anthropic**: la entrega el instructor o IT. Ofrecé dos opciones:
   - (recomendada) vos creás `.env` con la línea `ANTHROPIC_API_KEY=` vacía y ella la pega en el archivo con el editor (`code .env` si tiene VS Code, o el Bloc de notas / TextEdit);
   - o te la pega en el chat y vos la escribís en `.env`.
3. **TABLERO_URL** y **TABLERO_TOKEN**: los proyecta el instructor en la apertura. Son opcionales: si no los tiene, el avance queda guardado en la máquina y se envía después.

Escribí `.env` en la raíz del repo, partiendo de `.env.example`:

```
ANTHROPIC_API_KEY=<la key>
TABLERO_URL=<url o vacío>
TABLERO_TOKEN=<token o vacío>
```

Reglas con la key:
- **Nunca la repitas** en tus respuestas, ni completa ni en parte, ni la imprimas con `cat`, `type`, `echo` o similares.
- **Nunca la exportes en la shell** (`export`, `set`, `setx`, `$env:`): si queda como variable de entorno, Claude Code puede usarla en lugar de la cuenta de la persona. Va solo en `.env` y la leen los scripts de Python.
- No la escribas en ningún otro archivo.

Verificá que git ignora el `.env`:

```
git check-ignore .env
```

Tiene que imprimir `.env`. Si no imprime nada, agregá `.env` al `.gitignore` antes de seguir y volvé a verificar.

Guardá el alias:

```
<python del entorno> .claude/skills/marcar-avance/marcar.py --alias <alias>
```

(crea `.taller/alias`; si falla, escribí el alias solo en ese archivo).

## 6. Chequeo final

```
<python del entorno> check_setup.py
```

Hace una llamada mínima a la API (cuesta una fracción de centavo), lee las pólizas, verifica el modelo de embeddings y corre `steps/step-00/agente.py`. Imprime OK / PENDIENTE / FALLA por ítem con el arreglo sugerido.

Para cada FALLA: leé el arreglo que propone, aplicalo si podés y volvé a correr el chequeo. Los casos más comunes:

| Falla | Arreglo |
|-------|---------|
| La key no es válida | Que revise que la pegó completa, sin espacios ni comillas. |
| No hay conexión con api.anthropic.com | Proxy: ver `docs/setup.md`. Si hay un hotspot del celular disponible, probar con ese para confirmar que es la red. |
| Modelo de embeddings no descargado | Repetir el paso 4. |
| `.env` no ignorado | Paso 5. |
| Librerías | Repetir el paso 3 con el Python del entorno. |
| API key exportada en la terminal | Que cierre la terminal y abra una nueva; si sigue, que la saque de las variables de entorno del sistema. |

Cuando no quede ninguna FALLA, marcá el hito:

```
<python del entorno> .claude/skills/marcar-avance/marcar.py entorno_listo
```

## 7. Resumen

Terminá con una tabla corta, un ítem por fila, con OK o PENDIENTE:

- Git
- Python 3.11+
- Repo clonado y actualizado
- Entorno virtual y librerías
- Modelo de embeddings
- `.env` con la key (ignorado por git)
- Alias
- Tablero (TABLERO_URL)
- check_setup.py
- Hito entorno_listo

Para cada PENDIENTE, una línea con qué falta y quién lo resuelve (la persona, IT o el instructor).
