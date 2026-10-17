#!/usr/bin/env python3
"""Check pin-function and register/bit-field tables of output/<n>/<n>.md against
the words printed on the PDF page.

usage: python tools/check_struct_tables.py [--out reports/struct] [name ...]

Pin and register tables are outside tools/validate.py (no MIN/TYP/MAX). Here
every short cell of a row (pin number, name, type, bit range, field, reset,
access...; long description cells are skipped) must be printed on the same
visual line of the PDF page as the row's other short cells, and left to right in
the Markdown column order. A row is
  ok        all short cells found on one line (±3 pt), in column order;
  loose     found, but only within ±14 pt (vertically centred cells, wrapped
            names) or not in column order on a line;
  missing   a token of a short cell is not printed on the page (or the next);
  unpaired  every token exists on the page but never together on one line.
Only missing/unpaired rows need review; loose rows are reported as a count.

Pin descriptions written as prose ("**EN (Pin 1):** ...", Analog Devices/LTC
style) are checked too: the name and the pin list must be printed in that order
on the page (status "pin_prose").
Requires pymupdf. No network.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
KIND = re.compile(r"(?i)^(?:pin|pins|pin name|pin no\.?|no\.?|ball|bits?|bit\(s\)|bit name|field|name|symbol|"
                  r"reset|access|type|i/o|por value|por state|command name|cmd code|mnemonic|"
                  r"register|address|read/ ?write|pin type|pin number.*)$")
LONG = re.compile(r"(?i)description|function|operation|comment|remark|data format|ref page")
SEP = re.compile(r"^\|[\s:|-]+\|$")
TOK = re.compile(r"[^\W_]+")
GREEK = {"Omega": "Ω", "omega": "ω", "mu": "µ", "micro": "µ", "deg": "°"}


def plain(cell):
    cell = re.sub(r"<br\s*/?>", " ", cell)
    cell = re.sub(r"</?[A-Za-z][^>]*>", "", cell)
    cell = re.sub(r"\\?(?:overline|text|mathrm|mathbf|bar)\s*", "", cell)
    cell = re.sub(r"\\?\b(" + "|".join(GREEK) + r")\b", lambda m: GREEK[m[1]], cell)
    cell = cell.replace("\\_", "_").replace("\\", "")
    return re.sub(r"[*`${}]", "", cell).strip()


def squash(text):
    return "".join(TOK.findall(text.replace("μ", "µ"))).lower()


def tokens(cell):
    return [t.lower() for t in TOK.findall(plain(cell).replace("μ", "µ"))]


def md_tables(text):
    lines = text.splitlines(); page = 0; i = 0
    while i < len(lines):
        m = re.match(r"^\{(\d+)\}-{6,}", lines[i])
        if m:
            page = int(m[1]) + 1
        if lines[i].startswith("|") and i + 1 < len(lines) and SEP.match(lines[i + 1].strip()):
            header = [plain(c) for c in lines[i].strip().strip("|").split("|")]
            rows = []; j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append((j + 1, [c for c in lines[j].strip().strip("|").split("|")])); j += 1
            yield page, i + 1, header, rows
            i = j; continue
        i += 1


def structural(header):
    keys = [h for h in header if h and KIND.match(re.sub(r"\s*\(\d\)$", "", h.strip()))]
    if len(keys) == 1 and re.match(r"(?i)pin$", keys[0].strip()) and any(LONG.search(h) for h in header):
        return True  # "PIN | | DESCRIPTION": name and number under one spanning header
    return len(keys) >= 2 and any(re.match(r"(?i)pin|bit|ball|field|cmd|command|register|mnemonic|no", k) for k in keys)


def page_words(doc, page):
    out = []
    for p in (page, page + 1):
        if 1 <= p <= len(doc):
            for w in doc[p - 1].get_text("words"):
                t = squash(w[4])
                if t:
                    out.append((p, (w[1] + w[3]) / 2, w[0], t))
    return out


def check_row(cells, words):
    """cells: token lists of the short cells, in column order."""
    pages = {}
    for p, y, x, t in words:
        pages.setdefault(p, []).append((y, x, t))
    natural = "".join(t for _, _, _, t in words)  # pymupdf reading order keeps V+DD subscripts adjacent
    missing = sorted({t for c in cells for t in c if t not in natural})
    if missing:
        return "missing", missing

    def found(cell, text, pos=0):
        for t in cell:
            k = text.find(t, pos)
            if k < 0:
                return -1
            pos = k + len(t)
        return pos

    best = None
    for p, ws in pages.items():
        for y0 in sorted({round(y, 1) for y, _, _ in ws}):
            line = "".join(t for _, _, t in sorted((w for w in ws if abs(w[0] - y0) <= 3), key=lambda w: w[1]))
            pos = 0
            for c in cells:
                pos = found(c, line, pos)
                if pos < 0:
                    break
            if pos >= 0:
                return "ok", []
            if best:
                continue
            band = [w for w in ws if abs(w[0] - y0) <= 14]
            texts = [line,
                     "".join(t for _, _, t in sorted(band, key=lambda w: (w[1], w[0]))),
                     "".join(t for _, _, t in sorted(band, key=lambda w: (round(w[0]), w[1])))]
            if all(any(found(c, tx) >= 0 for tx in texts) for c in cells):
                best = "loose"
    return (best, []) if best else ("unpaired", [])


PROSE = re.compile(r"^\*\*(.{1,60}?\((?:Pins?|Balls?|Exposed)[^)]*\)):?\*\*")


def in_order(toks, text):
    pos = 0
    for t in toks:
        k = text.find(t, pos)
        if k < 0:
            return False
        pos = k + len(t)
    return True


def check(name):
    md = ROOT / "output" / name / f"{name}.md"
    doc = pymupdf.open(ROOT / f"{name}.pdf")
    result = {"tables": 0, "rows": 0, "ok": 0, "loose": 0, "issues": []}
    for page, line, header, rows in md_tables(md.read_text(encoding="utf-8")):
        if not structural(header):
            continue
        keep = [k for k, h in enumerate(header) if not LONG.search(h)]
        words = page_words(doc, page)
        result["tables"] += 1
        for ln, cells in rows:
            short = [tokens(cells[k]) for k in keep if k < len(cells) and len(plain(cells[k])) <= 40]
            short = [c for c in short if c]
            if len(short) < 2:
                continue
            result["rows"] += 1
            status, detail = check_row(short, words)
            if status in ("ok", "loose"):
                result[status] += 1
            else:
                result["issues"].append({"line": ln, "page": page, "status": status, "tokens": detail,
                                         "row": "|".join(plain(c) for c in cells)[:200]})
    page = 0
    for ln, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        m = re.match(r"^\{(\d+)\}-{6,}", line)
        if m:
            page = int(m[1]) + 1
        m = PROSE.match(line)
        if not m:
            continue
        toks = tokens(m[1])
        natural = "".join(t for _, _, _, t in page_words(doc, page))
        result["pin_prose"] = result.get("pin_prose", 0) + 1
        if not in_order(toks, natural):
            result["issues"].append({"line": ln, "page": page, "status": "pin_prose",
                                     "tokens": [t for t in toks if t not in natural], "row": plain(m[1])})
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("names", nargs="*"); ap.add_argument("--out", default="reports/struct")
    a = ap.parse_args()
    names = a.names or sorted(p.name for p in (ROOT / "output").iterdir() if (ROOT / f"{p.name}.pdf").exists())
    out = ROOT / a.out; out.mkdir(parents=True, exist_ok=True)
    summary = ["# Pin and register table check", "", "Rows: ok / loose / missing / unpaired.", "",
               "| datasheet | tables | rows | ok | loose | missing | unpaired | prose pin entries (not matched) |",
               "|---|---|---|---|---|---|---|---|"]
    for n in names:
        r = check(n)
        miss = sum(i["status"] == "missing" for i in r["issues"]); unp = len(r["issues"]) - miss
        prose = sum(i["status"] == "pin_prose" for i in r["issues"])
        summary.append(f"| {n} | {r['tables']} | {r['rows']} | {r['ok']} | {r['loose']} | {miss} | {unp - prose} | {r.get('pin_prose', 0)} ({prose}) |")
        (out / f"{n}.json").write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{n}: {r['tables']} tables, {r['rows']} rows, ok {r['ok']}, loose {r['loose']}, missing {miss}, "
              f"unpaired {unp - prose}, prose pin entries {r.get('pin_prose', 0)} ({prose} not matched)")
    (out / "SUMMARY.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
