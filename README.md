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
