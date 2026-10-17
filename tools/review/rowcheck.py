"""Print PDF words on the same visual line as a row label, with x positions, plus header column x positions.
usage: rowcheck.py pdf page(1-based) "label substring" [...]"""
import sys, pymupdf
pdf, page = sys.argv[1], int(sys.argv[2])
pg = pymupdf.open(pdf)[page-1]
words = pg.get_text("words")  # x0,y0,x1,y1,word,block,line,wno
lines = {}
for w in words:
    key = round((w[1]+w[3])/2/2.5)  # bucket by vertical center
    lines.setdefault(key, []).append(w)
def fmt(ws): return "  ".join(f"{w[4]}@{w[0]:.0f}" for w in sorted(ws, key=lambda w: w[0]))
for k in sorted(lines):
    t = " ".join(w[4] for w in sorted(lines[k], key=lambda w: w[0]))
    if any(h in t for h in ("MIN", "TYP", "MAX", "UNIT", "VALUE")) and len(t) < 80:
        print("HEADER y=%d:" % (k*2.5), fmt(lines[k]))
for label in sys.argv[3:]:
    for k in sorted(lines):
        t = " ".join(w[4] for w in sorted(lines[k], key=lambda w: w[0]))
        if label in t:
            for kk in (k-1, k, k+1):
                if kk in lines: print(f"[{label}] y={kk*2.5:.0f}:", fmt(lines[kk]))
