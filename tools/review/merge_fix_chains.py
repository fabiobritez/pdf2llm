"""Collapse chained fixes (A.new == B.old) into one old->final fix so apply_md_fixes stays idempotent."""
import json
from pathlib import Path
fp = Path("/srv/agents/pdf2llm/reports/review/fixes.json"); fx = json.loads(fp.read_text())
out = []
for b in fx:
    a = next((x for x in out if x["file"] == b["file"] and x["new"] and x["new"] == b["old"]), None)
    if a:
        a["new"] = b["new"]; a["evidence"] += " | Then: " + b["evidence"]
        a["sources"] = sorted(set(a["sources"]) | set(b["sources"])); a.setdefault("merged", []).append(b["id"])
    else:
        out.append(b)
fp.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n"); print(len(fx), "->", len(out))
