#!/usr/bin/env python3
"""Reconstruct table rows from PDF word coordinates using the MIN/TYP/MAX/UNIT header.

usage: pdfrows.py PDF PAGE(1-based) [y_from y_to]
Prints one line per visual row: param | conditions | marker | MIN | TYP | MAX | UNIT,
assigning words to columns by x-center relative to the header found on the page
(the header nearest above each row is used, so multi-table pages work).
"""
import sys
import pymupdf

HDR = {"MIN", "TYP", "MAX", "UNIT", "UNITS", "NOM", "VALUE"}


def main():
    pdf, page = sys.argv[1], int(sys.argv[2])
    y0, y1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (0, 1e9)
    pg = pymupdf.open(pdf)[page - 1]
    words = [w for w in pg.get_text("words")]
    lines = {}
    for w in words:
        lines.setdefault(round((w[1] + w[3]) / 2 / 3), []).append(w)
    headers = []  # (y, {name: xcenter}, cond_x)
    for k in sorted(lines):
        ws = sorted(lines[k], key=lambda w: w[0])
        names = {w[4].upper(): (w[0] + w[2]) / 2 for w in ws if w[4].upper() in HDR}
        if len(names) >= 2 and len(ws) <= 10:
            cond = [w[0] for w in ws if w[4].upper() in ("CONDITIONS", "CONDITION", "TEST")]
            headers.append((k * 3, names, cond[0] if cond else None))
    for k in sorted(lines):
        y = k * 3
        if not (y0 <= y <= y1):
            continue
        hs = [h for h in headers if h[0] <= y]
        if not hs:
            continue
        hy, names, cond_x = hs[-1]
        if hy == y:
            print(f"--- header y={y:.0f}: {names}")
            continue
        cols = sorted(names.items(), key=lambda kv: kv[1])
        first_x = cols[0][1] - 25
        bounds = [(n, (cols[i - 1][1] + x) / 2 if i else first_x) for i, (n, x) in enumerate(cols)]
        out = {"P": [], "C": [], "M": []}
        out.update({n: [] for n, _ in cols})
        for w in sorted(lines[k], key=lambda w: w[0]):
            xc = (w[0] + w[2]) / 2
            if xc < first_x:
                key = "C" if cond_x and w[0] >= cond_x - 2 else "P"
                if w[4] in ("l", "●"):
                    key = "M"
            else:
                key = [n for n, b in bounds if xc >= b][-1]
            out[key].append(w[4])
        cells = [" ".join(out["P"]), " ".join(out["C"]), " ".join(out["M"])] + [" ".join(out[n]) for n, _ in cols]
        print(f"y={y:4.0f} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
