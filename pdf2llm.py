#!/usr/bin/env python3

import argparse
from pathlib import Path

from datalab_sdk import ConvertOptions, DatalabClient


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_FORMATS = "markdown,html,json,chunks"


def pdfs_in_script_directory() -> list[Path]:
    """Return the PDF files located next to this script."""
    return sorted(
        (path for path in SCRIPT_DIR.iterdir() if path.is_file() and path.suffix.lower() == ".pdf"),
        key=lambda path: path.name.lower(),
    )


def select_pdf(pdf_argument: str | None, parser: argparse.ArgumentParser) -> Path:
    if pdf_argument:
        source = Path(pdf_argument).expanduser().resolve()
        if not source.is_file():
            parser.error(f"No existe el archivo: {source}")
        if source.suffix.lower() != ".pdf":
            parser.error(f"El archivo no es un PDF: {source}")
        return source

    pdfs = pdfs_in_script_directory()
    if not pdfs:
        parser.error(f"No hay archivos PDF en {SCRIPT_DIR}")
    if len(pdfs) > 1:
        choices = "\n  ".join(path.name for path in pdfs)
        parser.error(
            "Hay varios PDF. Indicá cuál querés convertir, por ejemplo:\n"
            f"  python3 {Path(__file__).name} {pdfs[0].name}\n\n"
            f"PDF disponibles:\n  {choices}"
        )
    return pdfs[0]


def convert_pdf(source: Path, destination: Path) -> Path:
    # Cada PDF tiene su propia carpeta para evitar mezclar archivos e imágenes.
    destination.mkdir(parents=True, exist_ok=True)

    # Datalab acepta varios formatos separados por comas en un único trabajo.
    options = ConvertOptions(
        output_format=OUTPUT_FORMATS,
        mode="accurate",
        paginate=True,
        disable_image_extraction=False,
        disable_image_captions=False,
        include_markdown_in_chunks=True,
    )

    client = DatalabClient()
    result = client.convert(str(source), options=options)
    result.save_output(destination / source.stem)

    return destination


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convierte un PDF con Datalab y guarda sus formatos por separado."
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        help="PDF a convertir. Se puede omitir cuando hay uno solo junto al script.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra qué se haría sin llamar a Datalab.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Omite la confirmación (útil para ejecución no interactiva).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Permite convertir otra vez aunque ya haya resultados.",
    )
    args = parser.parse_args()

    source = select_pdf(args.pdf, parser)
    destination = OUTPUT_DIR / source.stem

    print(f"PDF: {source}")
    print(f"Destino: {destination}")
    print(f"Formatos: {OUTPUT_FORMATS}")
    print("Costo: 1 trabajo de conversión de Datalab")

    if args.dry_run:
        print("Simulación terminada: no se llamó a Datalab.")
        return

    if destination.exists() and any(destination.iterdir()) and not args.force:
        parser.error(
            f"Ya hay resultados en {destination}. No se hizo ninguna llamada. "
            "Usá --force solamente si querés pagar una nueva conversión."
        )

    if not args.yes:
        try:
            answer = input("¿Enviar ahora este único trabajo a Datalab? [s/N]: ")
        except EOFError:
            parser.error("No se hizo ninguna llamada. Usá --yes para confirmar sin interacción.")
        if answer.strip().lower() not in {"s", "si", "sí"}:
            print("Cancelado: no se llamó a Datalab.")
            return

    print("Enviando 1 trabajo de conversión...")
    destination = convert_pdf(source, destination)
    print(f"Conversión terminada: {destination}")


if __name__ == "__main__":
    main()
