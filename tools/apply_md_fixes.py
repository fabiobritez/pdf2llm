#!/usr/bin/env python3
"""Apply reviewed, evidence-backed corrections to Datalab Markdown outputs.

Each entry of reports/review/fixes.json has: id, file, page (1-based PDF page),
old (exact text that must occur exactly once), new (replacement), evidence,
sources (who/what confirmed it) and severity.

The script is idempotent: an entry whose `old` text is absent but whose `new`
text is present is reported as already applied. Anything else (missing or
ambiguous `old`) aborts without writing, so fixes never land in the wrong place.

Usage: python3 tools/apply_md_fixes.py [--check] [fixes.json]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv
    fixes_path = Path(args[0]) if args else ROOT / "reports/review/fixes.json"
    fixes = json.loads(fixes_path.read_text(encoding="utf-8"))
    texts: dict[str, str] = {}
    status = []
    for fix in fixes:
        path = ROOT / fix["file"]
        text = texts.setdefault(fix["file"], path.read_text(encoding="utf-8"))
        count = text.count(fix["old"])
        if count == 1:
            texts[fix["file"]] = text.replace(fix["old"], fix["new"], 1)
            status.append(("apply", fix["id"]))
        elif count == 0 and fix["new"] and fix["new"] in text:
            status.append(("already", fix["id"]))
        elif count == 0 and not fix["new"]:
            status.append(("already", fix["id"]))
        else:
            print(f"ERROR {fix['id']}: old text found {count} times in {fix['file']}", file=sys.stderr)
            return 1
    for kind, fid in status:
        print(f"{kind:8} {fid}")
    if check_only:
        return 0
    for rel, text in texts.items():
        path = ROOT / rel
        if path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            print(f"wrote    {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
