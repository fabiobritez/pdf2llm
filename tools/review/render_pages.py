#!/usr/bin/env python3
"""Render PDF pages (full page + zoomed top/bottom crops) and slice the matching
Markdown page, as input for LLM image-vs-transcription review.

usage: render_pages.py OUTDIR name:page[,page...] [name:pages ...]
example: render_pages.py ~/work/pdf2llm-run/pages ina190:3,4,5,6 ltc3313:2,3,4,9
Requires pymupdf. Writes OUTDIR/<name>/p<N>.png, p<N>_top.png, p<N>_bottom.png, p<N>.md
"""
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[2]


def md_pages(name: str) -> dict[int, str]:
    folder = ROOT / "output" / name
    md = folder / f"{name}.md"
    if not md.exists():
        md = folder / "markdown.md"
    parts = re.split(r"^\{(\d+)\}-{10,}$", md.read_text(encoding="utf-8"), flags=re.M)
    return {int(parts[i]) + 1: parts[i + 1] for i in range(1, len(parts), 2)}


def main() -> None:
    out = Path(sys.argv[1]).expanduser()
    for spec in sys.argv[2:]:
        name, pages = spec.split(":")
        doc = pymupdf.open(ROOT / f"{name}.pdf")
        mds = md_pages(name)
        (out / name).mkdir(parents=True, exist_ok=True)
        for p in map(int, pages.split(",")):
            page = doc[p - 1]
            page.get_pixmap(dpi=200).save(out / name / f"p{p}.png")
            r = page.rect
            for tag, (y0, y1) in {"top": (0, 0.55), "bottom": (0.45, 1.0)}.items():
                clip = pymupdf.Rect(r.x0, r.height * y0, r.x1, r.height * y1)
                page.get_pixmap(dpi=300, clip=clip).save(out / name / f"p{p}_{tag}.png")
            (out / name / f"p{p}.md").write_text(mds[p], encoding="utf-8")
            print(f"{name} p{p}")


if __name__ == "__main__":
    main()
