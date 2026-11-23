# Guía de instalación y problemas frecuentes

Esta guía tiene dos partes: qué tiene que quedar instalado en cada notebook (para IT) y cómo resolver los problemas más comunes durante el setup (para participantes e instructor).

El camino normal es corto: IT instala Git, Python y Claude Code; el participante abre Claude Code en la carpeta del repo y pide **"preparame el entorno del taller"**. El skill hace el resto y termina corriendo `python check_setup.py`.

## 1. Lo que instala IT

| Programa | Versión | Windows | macOS |
|----------|---------|---------|-------|
| Git | última estable | `winget install --id Git.Git -e` o https://git-scm.com/download/win | `xcode-select --install` o `brew install git` |
| Python | 3.11, 3.12 o 3.13 (recomendado 3.12) | `winget install --id Python.Python.3.12 -e` o https://www.python.org/downloads/ (tildar "Add python.exe to PATH") | `brew install python@3.12` o https://www.python.org/downloads/ |
| Claude Code | última | `irm https://claude.ai/install.ps1 \| iex` (PowerShell) o `winget install Anthropic.ClaudeCode` | `curl -fsSL https://claude.ai/install.sh \| bash` o `brew install --cask claude-code` |
| Editor | Visual Studio Code recomendado | https://code.visualstudio.com | https://code.visualstudio.com |

Notas:

- Claude Code se instala con el **instalador nativo**: no necesita Node.js. (Si se instala por npm, hace falta Node.js 22 o superior.)
- En Windows, Claude Code requiere Windows 10 1809 o superior y no necesita administrador. Git for Windows es muy recomendable: con Git instalado, Claude Code usa Git Bash.
- Cada participante necesita una cuenta de Claude con un plan que incluya Claude Code (Pro, Max, Team, Enterprise o Console). El plan gratuito no lo incluye.
- La API key de Anthropic para los scripts del taller la entrega el instructor o IT. Va en el archivo `.env` del repo, nunca en el código ni en variables de entorno del sistema (ver sección 4.6).

Verificación rápida (5 minutos por notebook), en una terminal nueva:

```
git --version
python --version        (en Windows también: py --version)
claude --version
```

Después: `claude`, iniciar sesión con la cuenta del participante, clonar el repo y correr `python check_setup.py --offline`. Tiene que terminar sin ningún `[FALLA]`.

## 2. Red y proxy: dominios a habilitar

| Dominio | Para qué |
|---------|----------|
| `claude.ai`, `downloads.claude.ai`, `anthropic.com` | Instalación, login y uso de Claude Code |
| `api.anthropic.com` | Llamadas al modelo desde los scripts del taller |
| `github.com` (y `codeload.github.com`, `objects.githubusercontent.com`) | Descarga del repo |
| `pypi.org`, `files.pythonhosted.org` | Librerías de Python |
| `huggingface.co`, `cdn-lfs.huggingface.co`, `*.hf.co`, `*.xethub.hf.co` | Descarga del modelo de embeddings (la descarga redirige a los dominios CDN) |
| `script.google.com`, `script.googleusercontent.com` | Tablero de avance (la respuesta del tablero redirige al segundo dominio) |
| `elevenlabs.io` | Canal de voz del día 2 (opcional) |

## 3. Setup a mano (si no se puede usar el skill)

Desde la carpeta del repo:

**Windows (PowerShell o cmd)**

```
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"
copy .env.example .env
notepad .env
.venv\Scripts\python.exe check_setup.py
```

**macOS**

```
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"
cp .env.example .env
open -e .env
.venv/bin/python check_setup.py
```

En `.env` completá `ANTHROPIC_API_KEY=` (y, si el instructor los proyectó, `TABLERO_URL=` y `TABLERO_TOKEN=`). Guardá tu alias para el tablero:

```
python .claude/skills/marcar-avance/marcar.py --alias tu-alias
```

Comprobá que git ignora el `.env`: `git check-ignore .env` tiene que imprimir `.env`.

La instalación de librerías baja unos 800 MB (incluye torch) y el modelo de embeddings unos 470 MB. Conviene hacerlo antes del taller, con buena red.

## 4. Problemas frecuentes

### 4.1 Proxy corporativo

Síntomas: `pip` falla con `SSLError`, `CERTIFICATE_VERIFY_FAILED`, `ProxyError` o `Connection timed out`; `check_setup.py` dice "no hay conexión con api.anthropic.com".

1. Confirmá que es la red: probá con el hotspot del celular. Si así funciona, es el proxy.
2. Si la red usa un proxy explícito, agregalo al `.env` del repo (lo cargan los scripts de Python):

   ```
   HTTPS_PROXY=http://proxy.empresa:8080
   HTTP_PROXY=http://proxy.empresa:8080
   ```

   Para `pip`, pasalo en el comando: `python -m pip install --proxy http://proxy.empresa:8080 -r requirements.txt`.
3. Si el proxy inspecciona HTTPS con un certificado propio de la empresa, IT tiene que entregar ese certificado raíz (archivo `.pem` o `.crt`). Después, en `.env`:

   ```
   SSL_CERT_FILE=C:\certs\empresa.pem
   REQUESTS_CA_BUNDLE=C:\certs\empresa.pem
   ```

   y para pip: `python -m pip install --cert C:\certs\empresa.pem -r requirements.txt`.
4. Revisá que estén habilitados todos los dominios de la sección 2, incluidos los CDN de Hugging Face.

### 4.2 Rutas en Windows

- Cloná el repo en una ruta corta, sin espacios ni acentos y fuera de OneDrive: por ejemplo `C:\taller`. Las rutas largas rompen la instalación de torch ("No such file or directory" o "path too long"). Si no se puede acortar la ruta, IT puede habilitar las rutas largas de Windows (`LongPathsEnabled`).
- Si `python` abre la Microsoft Store o no hace nada, usá `py` (el lanzador de Python para Windows) o desactivá los "alias de ejecución de aplicaciones" de Python en la configuración de Windows.
- Si PowerShell no deja activar el entorno ("la ejecución de scripts está deshabilitada"), usá cmd (`.venv\Scripts\activate.bat`) o llamá directo a `.venv\Scripts\python.exe`. No hace falta cambiar la política de ejecución.
- En Git Bash las rutas van con `/`: `.venv/Scripts/python.exe check_setup.py`.

### 4.3 Descarga del modelo de embeddings (Hugging Face)

Síntoma: `check_setup.py` dice "Modelo de embeddings ... no está descargado".

- Corré el comando de descarga de la sección 3. Necesita `huggingface.co` **y** sus dominios CDN (`cdn-lfs.huggingface.co`, `*.hf.co`, `*.xethub.hf.co`). Si solo está habilitado `huggingface.co`, la descarga empieza y se corta.
- El modelo queda en la caché de Hugging Face (`%USERPROFILE%\.cache\huggingface` en Windows, `~/.cache/huggingface` en macOS). Si no hay forma de bajarlo en la red del cliente, se puede copiar esa carpeta desde otra máquina (por ejemplo, con un pendrive).
- `check_setup.py` nunca descarga nada: solo mira la caché.

### 4.4 Chroma y la telemetría

Chroma (la base vectorial del día 2) intenta mandar estadísticas de uso a internet. Detrás de un proxy eso genera errores que asustan pero no importan. Los scripts del taller la apagan; si ves mensajes sobre `posthog` o `telemetry`, agregá a `.env`:

```
ANONYMIZED_TELEMETRY=False
```

### 4.5 Librerías

- "No matching distribution found" o errores compilando paquetes: el Python no es 3.11 a 3.13. Volvé a crear el entorno con 3.12.
- `check_setup.py` dice "fuera del entorno virtual": activá `.venv` o usá su Python directo (`.venv\Scripts\python.exe` o `.venv/bin/python`).
- Instalación muy lenta: el antivirus revisa cada archivo de torch. Esperá; si se corta, repetí el mismo comando (pip retoma).

### 4.6 La API key nunca va en la terminal

La key vive **solo** en `.env`, y la leen los scripts de Python. Si está exportada como variable de entorno (en la terminal o en las variables del sistema), Claude Code puede usarla en lugar de la cuenta del participante, y el consumo de Claude Code pasa a cobrarse en esa key.

`check_setup.py` avisa si la encuentra exportada. Para sacarla:

- macOS: `unset ANTHROPIC_API_KEY` y borrá la línea `export ANTHROPIC_API_KEY=...` de `~/.zshrc` o `~/.bash_profile` si está.
- Windows: `Remove-Item Env:ANTHROPIC_API_KEY` en PowerShell para la sesión actual; si vuelve a aparecer, está en las variables de entorno del usuario o del sistema (Configuración → "Editar las variables de entorno") y hay que borrarla ahí.

Después, cerrá y abrí la terminal y Claude Code.

### 4.7 La API responde con error

| Mensaje | Qué pasa | Qué hacer |
|---------|----------|-----------|
| La key no es válida | Key incompleta, con espacios o comillas | Revisá la línea en `.env`: `ANTHROPIC_API_KEY=sk-ant-...` sin comillas |
| La API limitó el pedido | Muchos pedidos a la vez en la sala, o la key sin saldo | Esperá un minuto. Si sigue, avisale al instructor |
| No hay conexión con api.anthropic.com | Red o proxy | Sección 4.1 |

### 4.8 Tablero

Si `check_setup.py` dice que el tablero no responde, no bloquea el taller: los hitos se guardan en `.taller/pendientes.jsonl` y `marcar.py` los reenvía en la próxima corrida. Revisá que `TABLERO_URL` esté completa y que el proxy permita `script.google.com` y `script.googleusercontent.com`.
