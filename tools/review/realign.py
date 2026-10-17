#!/usr/bin/env python3
"""Propose corrected MIN/TYP/MAX/UNIT cells for md table rows from PDF word geometry.

For one PDF page, physical table rows ("bands") are rebuilt from word coordinates
under the MIN/TYP/MAX/UNIT header (LTC/TI/ADI layouts, incl. the ● full-temperature
marker column). Markdown rows of that page are then aligned to bands IN ORDER: each md
row takes the next band (within a small window) whose numeric values contain all of the
row's values. Rows whose cells differ from the band are reported as proposals.

This is a proposal generator for human/LLM-confirmed fixes, not an auto-fixer.

usage: realign.py NAME PAGE [--json out.json]
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[2]
LABELS = {"MIN": "MIN", "TYP": "TYP", "NOM": "NOM", "MAX": "MAX", "UNIT": "UNIT", "UNITS": "UNIT", "VALUE": "VALUE"}
VALUE_COLS = ("MIN", "TYP", "NOM", "MAX", "VALUE")
NUM = re.compile(r"(?<![\w.])[-–−+±]?\d+(?:[.,]\d+)*")
MARKERS = {"l", "●", "•"}


def nums(text):
    text = text.replace("$", "").replace("\\pm", "±").replace("\\times", "x")
    text = re.sub(r"<su[bp]>.*?</su[bp]>", "", text)
    text = re.sub(r"_\{[^}]*\}", "", text)
    text = re.sub(r"(?<=[A-Za-z}])([-–−+])(?=\d)", r" \1", text)  # fSW-10% -> fSW -10%
    out = []
    for t in NUM.findall(text):
        t = t.replace("–", "-").replace("−", "-").replace(",", "")
        sym = t.startswith("±")
        t = t.lstrip("±+")
        try:
            out.append(("±" if sym else "") + format(float(t), "g"))
        except ValueError:
            pass
    return out


def md_path(name):
    p = ROOT / "output" / name / f"{name}.md"
    return p if p.exists() else ROOT / "output" / name / "markdown.md"


def cells(line):
    return [c.strip() for c in line.strip()[1:-1].split("|")]


def pdf_bands(page):
    words = page.get_text("words")
    rows = {}
    for w in words:
        rows.setdefault(round((w[1] + w[3]) / 2 / 2), []).append(w)
    headers = []
    for k in sorted(rows):
        ws = rows[k]
        names = [(LABELS[w[4].upper()], (w[0] + w[2]) / 2) for w in ws
                 if w[4].upper() in LABELS and (w[4].isupper() or w[4] == w[4].capitalize())]
        if len({n for n, _ in names}) >= 2 and len(names) == len({n for n, _ in names}) and len(ws) <= 12:
            if any(n in VALUE_COLS for n, _ in names):
                y = k * 2
                if not headers or y - headers[-1]["y"] > 6:
                    cols = sorted(names, key=lambda c: c[1])
                    xs = [x for _, x in cols]
                    edges = [xs[0] - (xs[1] - xs[0]) / 2] + [(a + b) / 2 for a, b in zip(xs, xs[1:])]
                    tail = [w[0] for w in ws if w[0] > xs[-1] + 5 and re.match(r"(?i)(test|conditions?|comments?)", w[4])]
                    edges.append(min(tail) - 4 if tail else page.rect.width)
                    headers.append(dict(y=y, cols=[n for n, _ in cols], edges=edges))
    bands = []
    for hi, h in enumerate(headers):
        bottom = headers[hi + 1]["y"] if hi + 1 < len(headers) else page.rect.height - 30
        vals = [w for w in words if h["y"] + 4 < (w[1] + w[3]) / 2 < bottom
                and h["edges"][0] <= (w[0] + w[2]) / 2 < h["edges"][-1]]
        marks = [w for w in words if h["y"] + 4 < (w[1] + w[3]) / 2 < bottom and w[4] in MARKERS
                 and h["edges"][0] - 60 < (w[0] + w[2]) / 2 < h["edges"][0]]
        groups = []
        for w in sorted(vals, key=lambda w: (w[1] + w[3]) / 2):
            y = (w[1] + w[3]) / 2
            if groups and y - groups[-1]["y"] <= 4:
                groups[-1]["words"].append(w)
            else:
                groups.append(dict(y=y, words=[w]))
        for g in groups:
            band = dict(y=g["y"], header=hi, cells={c: "" for c in h["cols"]}, marker=False)
            for w in sorted(g["words"], key=lambda w: w[0]):
                xc = (w[0] + w[2]) / 2
                col = next(c for c, a, b in zip(h["cols"], h["edges"], h["edges"][1:]) if a <= xc < b)
                band["cells"][col] = (band["cells"][col] + " " + w[4]).strip()
            bands.append(band)
        for m in marks:
            my = (m[1] + m[3]) / 2
            cand = [b for b in bands if b["header"] == hi and -3 <= b["y"] - my <= 7]
            if cand:
                min(cand, key=lambda b: abs(b["y"] - my - 2))["marker"] = True
    return bands


def md_rows(name, page_no):
    lines = md_path(name).read_text(encoding="utf-8").splitlines()
    page, header, out = None, None, []
    for i, line in enumerate(lines):
        m = re.match(r"^\{(\d+)\}-{8,}", line)
        if m:
            page = int(m[1]) + 1
            header = None
            continue
        if page != page_no or not line.strip().startswith("|"):
            continue
        cs = cells(line)
        labels = [LABELS.get(re.sub(r"[^A-Za-z]", "", c).upper()) for c in cs]
        if sum(1 for l in labels if l in VALUE_COLS) >= 1 and any(labels):
            header = {i2: l for i2, l in enumerate(labels) if l}
            continue
        if header is None or set(line.strip()) <= set("|-: "):
            continue
        if len(cs) <= max(header):
            continue
        out.append(dict(line=i + 1, text=line, cells=cs, header=header))
    return out


def main():
    name, page_no = sys.argv[1], int(sys.argv[2])
    page = pymupdf.open(ROOT / f"{name}.pdf")[page_no - 1]
    bands = pdf_bands(page)
    rows = md_rows(name, page_no)
    proposals, unmatched = [], []
    pos = 0
    for r in rows:
        hdr = r["header"]
        vcols = {i: c for i, c in hdr.items() if c in VALUE_COLS or c == "UNIT"}
        tokens = [t for i in vcols for t in nums(r["cells"][i])] if vcols else []
        if not tokens:
            continue
        hit = None
        for j in range(pos, min(len(bands), pos + 8)):
            have = [t for c, v in bands[j]["cells"].items() if c in VALUE_COLS for t in nums(v)]
            pool = list(have)
            if all(t in pool and not pool.remove(t) for t in tokens):
                hit = j
                break
        if hit is None:
            unmatched.append(r["line"])
            continue
        pos = hit + 1
        b = bands[hit]
        new = list(r["cells"])
        md_marker = any("●" in r["cells"][i] for i in vcols)
        for i, c in vcols.items():
            if c == "UNIT":
                unit_txt = re.sub(r"^\s*[-–−+±]?\d+(?:\.\d+)?\s+", "", r["cells"][i]) if nums(r["cells"][i]) and re.match(r"^\s*[-–−+±]?\d", r["cells"][i]) else r["cells"][i]
                new[i] = unit_txt if unit_txt else b["cells"].get("UNIT", "")
                continue
            pdf_txt = b["cells"].get(c, "")
            md_txt = r["cells"][i].replace("●", "").strip()
            # keep md formatting when it carries the same numbers as the PDF cell
            new[i] = md_txt if nums(md_txt) == nums(pdf_txt) and md_txt else pdf_txt.replace("-", "–") if pdf_txt.startswith("-") else pdf_txt
            if not nums(pdf_txt) and not nums(md_txt) and md_txt:
                new[i] = md_txt
        # values moved from another md cell: reuse md formatting for that number
        keys = [tuple(nums(r["cells"][i].replace("●", ""))) for i in vcols if hdr[i] != "UNIT"]
        md_cells_by_nums = {tuple(nums(r["cells"][i].replace("●", ""))): r["cells"][i].replace("●", "").strip()
                            for i in vcols if hdr[i] != "UNIT" and keys.count(tuple(nums(r["cells"][i].replace("●", "")))) == 1}
        for i, c in vcols.items():
            if c != "UNIT" and tuple(nums(new[i])) in md_cells_by_nums and nums(new[i]):
                new[i] = md_cells_by_nums[tuple(nums(new[i]))]
        min_i = next((i for i, c in vcols.items() if c == "MIN"), None)
        if min_i is not None and b["marker"]:
            new[min_i] = ("● " + new[min_i]).strip()
        elif min_i is not None and md_marker and not b["marker"]:
            pass  # marker removal is reported separately; keep md marker
        if [x.strip() for x in new] != [x.strip() for x in r["cells"]]:
            proposals.append(dict(line=r["line"], old=r["text"], new="| " + " | ".join(new) + " |",
                                  pdf=b["cells"], pdf_marker=b["marker"], md_marker=md_marker))
    out = dict(name=name, page=page_no, proposals=proposals, unmatched_md_lines=unmatched,
               rows_checked=len(rows))
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for p in proposals:
        print(f"L{p['line']}  marker pdf={p['pdf_marker']} md={p['md_marker']}\n  - {' '.join(p['old'].split())[:230]}\n  + {p['new'][:230]}")
    print(f"rows={len(rows)} proposals={len(proposals)} unmatched={unmatched}")


if __name__ == "__main__":
    main()
