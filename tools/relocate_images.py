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
    md_refs = re.findall(r"!\[[^\]]*\]\(img/(" + NAME + r")\)", md.read_text(encoding="utf-8"))
    orphans = sorted(on_disk - set(md_refs))
    if orphans:
        problems.append(f"{len(orphans)} images not referenced by {md.name}, e.g. {orphans[0]}")
    html = html_export(folder)
    if html:
        html_refs = re.findall(r'src="img/(' + NAME + r')"', html.read_text(encoding="utf-8"))
        common = set(md_refs) & set(html_refs)
        a = [r for r in md_refs if r in common]
        b = [r for r in html_refs if r in common]
        if a != b:
            k = next(i for i, (x, y) in enumerate(zip(a, b)) if x != y)
            problems.append(f"image order differs from {html.name} at #{k}: md {a[k]} vs html {b[k]}")
        only_html = sorted(set(html_refs) - set(md_refs))
        if only_html:
            problems.append(f"{len(only_html)} images in {html.name} but not in {md.name}, e.g. {only_html[0]}")
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
