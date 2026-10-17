#!/usr/bin/env python3
"""Reproduce every output/<n>/<n>.md from the original Datalab conversion.

usage: python3 tools/replay_fixes.py

Starting from the conversion as committed in 6439792, apply
reports/review/fixes.json in order and then the image relocation to img/
(tools/relocate_images.py). The result must equal the working-tree .md byte
for byte; exit 1 otherwise. tps6287b20's Markdown was named markdown.md in
that commit.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import relocate_images  # noqa: E402

BASE = "6439792"
RENAMED = {"output/tps6287b20/tps6287b20.md": "output/tps6287b20/markdown.md"}


def main() -> int:
    fixes = json.loads((ROOT / "reports/review/fixes.json").read_text(encoding="utf-8"))
    files = sorted({f["file"] for f in fixes} | {str(p.relative_to(ROOT)) for p in (ROOT / "output").glob("*/*.md")
                                                  if not p.name.endswith(".llm.md")})
    bad = 0
    for name in files:
        text = subprocess.run(["git", "show", f"{BASE}:{RENAMED.get(name, name)}"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
        for fix in (f for f in fixes if f["file"] == name):
            if fix["new"] and fix["old"] in fix["new"] and text.count(fix["new"]) == 1:
                continue
            if text.count(fix["old"]) != 1:
                print(f"FAIL {fix['id']}: old text found {text.count(fix['old'])} times"); bad += 1; break
            text = text.replace(fix["old"], fix["new"], 1)
        text = relocate_images.BARE.sub(r"img/\1", text)
        if text != (ROOT / name).read_text(encoding="utf-8"):
            print(f"DIFF {name}"); bad += 1
    print(f"replay {BASE} + fixes.json ({len(fixes)} fixes) + img/ relocation: {len(files)} files, {bad} differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
