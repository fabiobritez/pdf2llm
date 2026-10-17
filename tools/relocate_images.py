#!/usr/bin/env python3
"""Move a datasheet's Datalab images into output/<name>/img/ and point the
Markdown references there; then audit the image references.

usage: python3 tools/relocate_images.py [--check] name [name ...]

The move uses `git mv` (history is kept). Rewriting is idempotent: only bare
`<hash>_img.<ext>` names not already prefixed by a path are changed. The audit
(also run with --check, without changing anything) verifies that:
  - every image referenced by <name>.md or <name>.llm.md exists under img/;
  - every image file under img/ is referenced by the full Markdown (no orphans);
  - the .llm.md references exactly the .md images minus dropped cover icons, in
    the same order.
Image positions were checked against Datalab's HTML export before that export
was removed (commit e8b4963); the .md is now the source of truth.
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


def full_markdown(folder: Path) -> Path:
    path = folder / f"{folder.name}.md"
    if not path.exists():
        raise SystemExit(f"no {path.name} in {folder}")
    return path


def text_files(folder: Path):
    return [full_markdown(folder)]


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
    orphans = sorted(on_disk - set(md_refs))
    if orphans:
        problems.append(f"{len(orphans)} images not referenced by {md.name}, e.g. {orphans[0]}")
    llm = folder / f"{folder.name}.llm.md"
    if llm.exists():
        llm_refs = re.findall(r"img/(" + NAME + r")", llm.read_text(encoding="utf-8"))
        missing = sorted(set(llm_refs) - on_disk)
        if missing:
            problems.append(f"{llm.name}: {len(missing)} referenced images missing, e.g. {missing[0]}")
        kept = [r for r in dict.fromkeys(md_refs) if r in set(llm_refs)]
        if list(dict.fromkeys(llm_refs)) != kept:
            problems.append(f"{llm.name}: image order differs from {md.name}")
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
