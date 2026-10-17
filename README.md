# pdf2llm

Utilidad de línea de comandos para convertir archivos PDF a Markdown, HTML,
JSON y fragmentos (`chunks`) mediante la API de Datalab.

## Requisitos

- Python 3.10 o posterior.
- Una clave de API de Datalab.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATALAB_API_KEY="tu_clave"
```

## Uso

Primero se puede validar la operación sin consumir un trabajo de la API:

```bash
python3 pdf2llm.py documento.pdf --dry-run
```

Para convertir el documento:

```bash
python3 pdf2llm.py documento.pdf
```

El programa pide confirmación antes de enviar el trabajo. `--yes` omite esa
confirmación y `--force` permite reemplazar una conversión existente; ambas
opciones pueden generar un nuevo consumo en la API.

Los resultados se guardan en `output/<nombre-del-pdf>/`. Los PDF usados como
fuente y sus conversiones se versionan únicamente para consulta interna durante el
desarrollo. Los fabricantes conservan los derechos sobre los datasheets y sobre el
contenido extraído; este repositorio debe mantenerse privado y no concede una
licencia sobre ese material. Los entornos virtuales y los archivos `.env` quedan
fuera de Git.

## Salida por datasheet

`output/<n>/` contiene:

- `<n>.md`: transcripción completa y literal del datasheet. Sobre la conversión original solo tiene tres cosas: las correcciones verificadas de `reports/review/fixes.json`, las rutas de imagen pasadas a `img/` y los epígrafes de figura que faltaban. Para reproducirlo, aplicar `fixes.json` sobre el commit 6439792 y luego `tools/relocate_images.py`.
- `<n>.llm.md`: versión compacta para LLM, generada con `tools/llm_compact.py`. Empieza con un resumen de características clave y funcionamiento general, redactado por un modelo, verificado afirmación por afirmación por un segundo modelo y con todos los números comprobados contra el datasheet. Luego van un índice de secciones y el detalle compacto. Las figuras aparecen como "description only, not data".
- `img/`: imágenes referenciadas desde el `.md`, el `.html`, el `.json` y los chunks.
- `.html`, `.json` y `.chunks.json`: exportaciones originales. Solo se les cambiaron las rutas de imagen; no llevan las correcciones de transcripción.

Comprobaciones:

```
python3 tools/relocate_images.py --check <n>       # imágenes: sin huérfanas, orden igual al HTML
python tools/check_llm_fidelity.py                 # tablas de especificaciones y números del .llm.md
python tools/validate.py --all                     # tablas contra la geometría del PDF
uv run --no-project --with tiktoken python tools/token_counts.py
```
