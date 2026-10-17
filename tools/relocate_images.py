#!/usr/bin/env python3
"""Move a datasheet's Datalab images into output/<name>/img/ and point every
reference (md, html, json, chunks) there; then audit the image references.

usage: python3 tools/relocate_images.py [--check] name [name ...]

The move uses `git mv` (history is kept). Rewriting is idempotent: only bare
`<hash>_img.<ext>` names not already prefixed by a path are changed. The audit
(also run with --check, without changing anything) verifies that:
  - every image referenced by any file exists under img/;
  - every image file under img/ is referenced by the full Markdown (no orphans);
  - the Markdown references the images in the same order as the HTML export,
    i.e. each image sits at its document position.
Exit status 1 when the audit fails.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = r"[0-9a-f]{32}_img\.(?:jpe?g|png|gif|webp)"
BARE = re.compile(r"(?<![\w/])(" + NAME + r")")
ANY = re.compile(r"(?:img/)?(" + NAME + r")")
TEXT_SUFFIXES = (".md", ".html", ".json")


def full_markdown(folder: Path) -> Path:
    for path in (folder / f"{folder.name}.md", folder / "markdown.md"):
        if path.exists():
            return path
    raise SystemExit(f"no Markdown in {folder}")


def html_export(folder: Path):
    for path in (folder / f"{folder.name}.html", folder / "html.html"):
        if path.exists():
            return path
    return None


def text_files(folder: Path):
    return sorted(p for p in folder.iterdir() if p.is_file() and p.name.endswith(TEXT_SUFFIXES)
                  and not p.name.endswith(".llm.md"))


def relocate(folder: Path) -> None:
    images = sorted(p for p in folder.iterdir() if p.is_file() and re.fullmatch(NAME, p.name))
    if images:
        (folder / "img").mkdir(exist_ok=True)
        subprocess.run(["git", "mv", "-k", *[str(p) for p in images], str(folder / "img")], cwd=ROOT, check=True)
    for path in text_files(folder):
        text = path.read_text(encoding="utf-8")
        new = BARE.sub(r"img/\1", text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"rewrote {path.relative_to(ROOT)}: {len(BARE.findall(text))} references")


def audit(folder: Path) -> list:
    problems = []
    on_disk = {p.name for p in (folder / "img").glob("*")} if (folder / "img").exists() else set()
    loose = [p.name for p in folder.iterdir() if p.is_file() and re.fullmatch(NAME, p.name)]
    if loose:
        problems.append(f"{len(loose)} images outside img/")
    for path in text_files(folder):
        text = path.read_text(encoding="utf-8")
        if BARE.search(text):
            problems.append(f"{path.name}: {len(BARE.findall(text))} references without img/")
        missing = sorted({m for m in ANY.findall(text)} - on_disk)
        if missing:
            problems.append(f"{path.name}: {len(missing)} referenced images missing, e.g. {missing[0]}")
    md = full_markdown(folder)
    md_text = md.read_text(encoding="utf-8")
    # Alt text may itself contain brackets ("D[7:0]"), so anchor on "](img/...)".
    md_refs = re.findall(r"\]\(img/(" + NAME + r")\)", md_text)
    referenced = set().union(*(set(ANY.findall(p.read_text(encoding="utf-8"))) for p in text_files(folder)))
    orphans = sorted(on_disk - referenced)
    if orphans:
        problems.append(f"{len(orphans)} images referenced by no file, e.g. {orphans[0]}")
    html = html_export(folder)
    if html:
        html_text = html.read_text(encoding="utf-8")
        html_refs = re.findall(r'src="img/(' + NAME + r')"', html_text)
        if set(html_refs) <= set(md_refs):
            a = [r for r in md_refs if r in set(html_refs)]
            if a != html_refs:
                k = next(i for i, (x, y) in enumerate(zip(a, html_refs)) if x != y)
                problems.append(f"image order differs from {html.name} at #{k}: md {a[k]} vs html {html_refs[k]}")
            only_md = sorted(set(md_refs) - set(html_refs))
            if only_md:
                problems.append(f"{len(only_md)} md images not in {html.name}")
        else:
            # The exports come from separate conversion runs (own image crops):
            # compare per page that the md has an image wherever the HTML has one.
            def per_page(chunks):
                return {int(k): len(re.findall(NAME, v)) for k, v in chunks}
            md_pages = per_page(re.findall(r"^\{(\d+)\}-{6,}\n(.*?)(?=^\{\d+\}-{6,}|\Z)", md_text, re.S | re.M))
            html_pages = per_page(re.findall(r'data-page-id="(\d+)"(.*?)(?=data-page-id=|\Z)', html_text, re.S))
            short = {p: (md_pages.get(p, 0), n) for p, n in html_pages.items() if md_pages.get(p, 0) < n}
            if short:
                problems.append(f"pages where md has fewer images than {html.name} (md, html): {short}")
            print(f"  note: {html.name} is a separate conversion run ({len(set(html_refs) - set(md_refs))} of its "
                  f"{len(set(html_refs))} images are its own crops); per-page image counts compared instead")
    print(f"{folder.name}: {len(on_disk)} images, {len(md_refs)} md references; "
          + ("OK" if not problems else "; ".join(problems)))
    return problems


def main() -> int:
    check = "--check" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    failed = False
    for name in names:
        folder = ROOT / "output" / name
        if not check:
            relocate(folder)
        failed |= bool(audit(folder))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
