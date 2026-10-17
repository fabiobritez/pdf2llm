#!/usr/bin/env python3
"""Deterministic, offline checks of datasheet Markdown against PDF page text."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
WORD_THRESHOLD = 0.85
NUMBER_THRESHOLD = 0.80
ALIGNMENT_MARGIN = 0.18
LIST_LIMIT = 40
ISSUE_TYPES = ("missing unit", "unit in wrong column", "column shift", "ordering", "ragged row")
MARKER = re.compile(r"^\{(\d+)\}-{8,}\s*$", re.M)
IMAGE = re.compile(r"!\[((?:\\.|[^\]\\])*)\]\([^\n]*?\)")
NUMBER = re.compile(r"(?<![\d.])(?P<sign>\+-|[+-])?(?P<value>\d+(?:\.\d+)?|\.\d+)(?P<percent>\s*%)?")
UNIT = re.compile(r"(?<![A-Za-z])(?:ppm/degC|[mun]?V/[mun]?s|[mun]?V/V|V/V|[mun]?V|[mun]?A|%|dB|[kM]?Hz|[num]?s|[kmM]?ohm|[pnu]?F|degC|[mu]?W)(?![A-Za-z0-9])")


def normalize(text: str) -> str:
    """Flatten common Markdown, HTML and LaTeX typography on either side."""
    text = html.unescape(text)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"</?[A-Za-z][^>]*>", " ", text)
    for old, new in ((r"\mu", "u"), ("μ", "u"), ("µ", "u"),
                     (r"\pm", "+-"), ("±", "+-"), (r"\circ", "deg"),
                     ("°", "deg"), (r"\times", "x"), ("×", "x"),
                     (r"\Omega", "ohm"), ("Ω", "ohm")):
        text = text.replace(old, new)
    text = text.translate(str.maketrans({"–": "-", "−": "-", "‑": "-", "\u00ad": ""}))
    text = re.sub(r"([A-Za-z])-\s*\n\s*([a-z])", r"\1\2", text)
    text = re.sub(r"\\(?:text|mathrm|mathbf|mathit|operatorname)\s*", "", text)
    text = re.sub(r"\\(?:left|right|quad|qquad)\b|\\[,;!]", " ", text)
    text = re.sub(r"[\^_{}$]", "", text)
    text = text.replace("\\", "")
    text = re.sub(r"(\+-|[+-])\s+(?=\d)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def numbers(text: str) -> set[str]:
    """Canonical decimal tokens; explicit + and trailing zeroes are immaterial.

    Expand ± into both signed endpoints. Digits in part names count too, since
    losing a pin/part suffix is useful evidence. Percent suffixes are preserved.
    """
    result = set()
    for match in NUMBER.finditer(text):
        try:
            value = Decimal(match['value'])
        except InvalidOperation:
            continue
        suffix = "%" if match['percent'] else ""
        signs = (-1, 1) if match['sign'] == "+-" else (-1,) if match['sign'] == "-" else (1,)
        for sign in signs:
            token = format(value * sign, "f")
            if "." in token:
                token = token.rstrip("0").rstrip(".")
            result.add(("0" if token in ("-0", "") else token) + suffix)
    return result


def tokens(text: str) -> tuple[set[str], set[str]]:
    text = normalize(text)
    return set(re.findall(r"[a-z]{3,}", text.lower())), numbers(text)


def coverage(source: set[str], target: set[str]) -> float:
    return len(source & target) / len(source) if source else 1.0


def split_pages(text: str) -> tuple[dict[int, str], list[str]]:
    matches = list(MARKER.finditer(text))
    pages, warnings = {}, []
    if not matches:
        return {0: text}, ["No page markers; all Markdown assigned to page 1"]
    if text[:matches[0].start()].strip():
        warnings.append("Content before first marker assigned to first marked page")
    for index, match in enumerate(matches):
        page = int(match[1])
        body = text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)]
        if index == 0:
            body = text[:match.start()] + body
        if page in pages:
            warnings.append(f"Duplicate marker {{{page}}}; contents combined")
        pages[page] = pages.get(page, "") + body
    return pages, warnings


def pdf_text(page: pymupdf.Page, path: Path, index: int) -> str:
    text = page.get_text()
    # Poppler only for empty/broken extraction, keeping ordinary runs fast.
    if len(re.findall(r"[A-Za-z0-9]", text)) < 30:
        binary = Path.home() / ".local/bin/pdftotext"
        if binary.is_file():
            try:
                other = subprocess.run([str(binary), "-layout", "-f", str(index + 1),
                                        "-l", str(index + 1), str(path), "-"],
                                       capture_output=True, text=True, timeout=15, check=True).stdout
                if len(other.strip()) > len(text.strip()):
                    text = other
            except (OSError, subprocess.SubprocessError):
                pass
    return text


def figure_reasons(pdf: str, md: str) -> list[str]:
    """Conservative image/axis heuristics, independent of coverage scores."""
    reasons = []
    images = list(IMAGE.finditer(md))
    visible = normalize(IMAGE.sub("", md))
    alt_size = sum(len(normalize(m[1])) for m in images)
    has_table = bool(re.search(r"^\s*\|.*\|", md, re.M) or "<table" in md.lower())
    if not has_table and images and len(visible.split()) < 160 and alt_size > len(visible):
        reasons.append("image-dominated Markdown")
    short = []
    for line in pdf.splitlines():
        line = normalize(line)
        if re.fullmatch(r"[+-]?\d{1,4}(?:\.\d{1,3})?%?", line):
            short.append(float(line.rstrip("%")))
    # Several evenly spaced ticks, plus a substantial population of isolated
    # numeric labels, distinguish plots from prose with a few page numbers.
    values = sorted(set(short))
    regular = False
    for start in range(len(values)):
        for following in range(start + 1, min(start + 8, len(values))):
            step = values[following] - values[start]
            if step > 0 and sum(any(abs(v - (values[start] + step * k)) < 1e-6
                                    for v in values) for k in range(6)) == 6:
                regular = True
                break
        if regular:
            break
    if not has_table and len(short) >= 35 and regular and len(short) / max(1, len(pdf.splitlines())) > 0.18:
        reasons.append("many isolated numeric labels with regular axis ticks")
    return reasons


class HTMLTables(HTMLParser):
    """Collect simple HTML tables with source line numbers (including spans)."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.rows, self.cells, self.buffer = [], None, None, None
        self.pending = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self.rows, self.pending = [], {}
        elif tag == "tr" and self.rows is not None:
            self.cells, self.line, self.col = [], self.getpos()[0], 0
        elif tag in ("td", "th") and self.cells is not None:
            self.buffer = []
            self.span = tuple(max(1, min(100, int(attrs.get(a, "1"))))
                              if attrs.get(a, "1").isdigit() else 1 for a in ("rowspan", "colspan"))
        elif tag == "br" and self.buffer is not None:
            self.buffer.append(" ")

    def handle_data(self, data):
        if self.buffer is not None:
            self.buffer.append(data)

    def inherited(self):
        while self.col in self.pending:
            value, remaining = self.pending.pop(self.col)
            self.cells.append(value)
            if remaining > 1:
                self.pending[self.col] = (value, remaining - 1)
            self.col += 1

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.buffer is not None:
            self.inherited()
            value = "".join(self.buffer).strip()
            rowspan, colspan = self.span
            for _ in range(colspan):
                self.cells.append(value)
                if rowspan > 1:
                    self.pending[self.col] = (value, rowspan - 1)
                self.col += 1
            self.buffer = None
        elif tag == "tr" and self.cells is not None:
            self.inherited()
            self.rows.append((self.line, self.cells))
            self.cells = None
        elif tag == "table" and self.rows is not None:
            self.tables.append(self.rows)
            self.rows = None


def table_blocks(text: str) -> list[list[tuple[int, list[str]]]]:
    blocks, current = [], []
    for line_no, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            if not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in cells):
                current.append((line_no, cells))
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    parser = HTMLTables()
    parser.feed(text)
    return sorted(blocks + parser.tables, key=lambda block: block[0][0] if block else 0)


def interval(cell: str):
    """Only compare plain numeric cells with optional %, never expressions."""
    match = re.fullmatch(r"(\+-|[+-])?(\d+(?:\.\d+)?|\.\d+)\s*(%)?", cell)
    if not match:
        return None
    value = Decimal(match[2])
    if match[1] == "+-":
        return (-value, value, match[3])
    value *= -1 if match[1] == "-" else 1
    return (value, value, match[3])


def symbolic(cell: str) -> bool:
    """Recognize supply-relative limits, not assignments or condition prose."""
    compact = re.sub(r"\s+", "", cell)
    if compact in ("Float", "Open", "GND") or re.fullmatch(r"[+-]?[\d.]+REF", compact):
        return True
    # VREF, V_IN, V+ and GND are legitimate limits. An equals sign, device
    # selector (A1), range prose or an unknown word remains a shift candidate.
    expression = re.sub(r"(?:[A-Z]*V[A-Za-z0-9]*|[IRCTf][A-Z][A-Za-z0-9]*|t\d+|GND)", "1", compact)
    return expression != compact and bool(re.fullmatch(r"[\d.()+*/x+-]+", expression))


def table_issues(text: str) -> list[dict]:
    issues = []
    marker_lines = [(text.count("\n", 0, m.start()) + 1, int(m[1]) + 1) for m in MARKER.finditer(text)]

    def emit(kind, row, detail):
        line, cells = row
        page = next((p for n, p in reversed(marker_lines) if n <= line), 1)
        issues.append(dict(type=kind, page=page, line=line, detail=detail,
                           row=(" | ".join(cells))[:240]))

    for block in table_blocks(text):
        header, rows, groups = None, [], []
        for row in block:
            cells = [normalize(c) for c in row[1]]
            labels = [c.upper().strip(" .:") for c in cells]
            value_cols = [i for i, c in enumerate(labels) if c in ("MIN", "TYP", "MAX", "NOM")]
            unit_cols = [i for i, c in enumerate(labels) if c in ("UNIT", "UNITS")]
            if value_cols:
                if header is not None:
                    groups.append((header, rows))
                header = (len(cells), value_cols, unit_cols, labels)
                rows = []
            elif header is not None:
                rows.append((row, cells))
        if header is not None:
            groups.append((header, rows))
        for (width, value_cols, unit_cols, labels), rows in groups:
            # Build parameter groups before checking units: a later continuation
            # can carry the shared unit. Conditions do not define a parameter.
            parameter_cols = [0] if min(value_cols) > 0 else []
            if min(value_cols) > 1 and not labels[1]:
                parameter_cols.append(1)
            parameter_groups, group, previous = [], [], None
            for row, cells in rows:
                if len(cells) != width:
                    emit("ragged row", row, f"{len(cells)} cells; header has {width}")
                    continue
                key = tuple(cells[i] for i in parameter_cols)
                if any(key) and key != previous:
                    if group:
                        parameter_groups.append(group)
                    group = []
                    previous = key
                group.append((row, cells))
            if group:
                parameter_groups.append(group)
            for group in parameter_groups:
                has_unit = any(cells[i] for _, cells in group for i in unit_cols)
                for row, cells in group:
                    values = [cells[i] for i in value_cols]
                    if unit_cols and not has_unit and any(numbers(v) for v in values):
                        emit("missing unit", row, "No unit in this parameter group")
                    misplaced = [labels[i] for i in value_cols
                                 if UNIT.search(cells[i]) and not symbolic(cells[i])]
                    misplaced += [labels[i] for i in unit_cols
                                  if re.search(r"(?<![A-Za-z])[-+]?\d", re.sub(r"<su[bp]>.*?</su[bp]>", "", row[1][i], flags=re.I))]
                    if misplaced:
                        emit("unit in wrong column", row, "Check " + ", ".join(misplaced))
                    shifted = []
                    for i in value_cols:
                        value = cells[i]
                        # Units alone are handled above. Expressions with variable
                        # names or prose remain reviewable condition/shift warnings.
                        residue = UNIT.sub("", value)
                        residue = re.sub(r"(?<=\d)[pnumkMG]\b", "", residue)
                        if re.search(r"[A-Za-z]", residue) and not symbolic(value):
                            shifted.append(labels[i])
                    if shifted:
                        emit("column shift", row, "Text/expression in " + ", ".join(shifted))
                    parsed = {labels[i]: interval(cells[i]) for i in value_cols}
                    bad = []
                    for lo, hi in (("MIN", "TYP"), ("TYP", "MAX"), ("MIN", "MAX"),
                                   ("MIN", "NOM"), ("NOM", "MAX")):
                        a, b = parsed.get(lo), parsed.get(hi)
                        # Negative magnitude limits often reverse algebraic order.
                        if a and b and a[1] < 0 and b[1] < 0:
                            continue
                        if a and b and a[2] == b[2] and a[0] > b[1]:
                            bad.append(f"{lo} > {hi}")
                    if bad:
                        emit("ordering", row, ", ".join(bad))
    return sorted(issues, key=lambda item: (item['line'], item['type'], item['detail']))


def locate_md(name: str) -> Path:
    folder = ROOT / "output" / name
    for path in (folder / f"{name}.md", folder / "markdown.md"):
        if path.is_file():
            return path
    candidates = sorted(folder.glob("*.md"))
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError(f"{name}: expected a named Markdown file or exactly one *.md")


def validate(name: str) -> dict:
    md_path = locate_md(name)
    text = md_path.read_text(encoding="utf-8")
    md_pages, warnings = split_pages(text)
    with pymupdf.open(ROOT / f"{name}.pdf") as document:
        pdf_pages = [pdf_text(page, ROOT / f"{name}.pdf", i) for i, page in enumerate(document)]
    pdf_tokens = [tokens(page) for page in pdf_pages]
    pages = []
    for index in sorted(set(range(len(pdf_pages))) | set(md_pages)):
        raw = md_pages.get(index, "")
        clean = IMAGE.sub("", raw)
        words, nums = tokens(clean)
        alts = numbers(normalize(" ".join(m[1] for m in IMAGE.finditer(raw)))) - nums
        source_words, source_nums = pdf_tokens[index] if index < len(pdf_pages) else (set(), set())
        wc, nc = coverage(source_words, words), coverage(source_nums, nums)
        flags = []
        reasons = figure_reasons(pdf_pages[index], raw) if index < len(pdf_pages) else []
        if index not in md_pages:
            flags.append("missing Markdown page")
            reasons = []
        if index >= len(pdf_pages):
            flags.append("Markdown page has no PDF page")
        if not source_words and not source_nums:
            flags.append("no extractable PDF tokens")
        if source_words or source_nums:
            own_score = (wc + nc) / 2
            for neighbor in (index - 1, index + 1):
                if 0 <= neighbor < len(pdf_tokens):
                    nw, nn = pdf_tokens[neighbor]
                    score = (coverage(nw, words) + coverage(nn, nums)) / 2
                    if len(nw) >= 10 and score >= 0.65 and score > own_score + ALIGNMENT_MARGIN:
                        flags.append(f"alignment: Markdown matches PDF page {neighbor + 1} better ({score:.0%} vs {own_score:.0%})")
        low = wc < WORD_THRESHOLD or nc < NUMBER_THRESHOLD
        classification = "figure" if reasons else "text loss" if low else "text"
        if flags and not reasons:
            classification = "text loss"
        pages.append(dict(page=index + 1, word_coverage=wc, number_coverage=nc,
                          pdf_word_tokens=len(source_words), pdf_number_tokens=len(source_nums),
                          missing_numbers=sorted(source_nums - nums)[:LIST_LIMIT],
                          missing_number_count=len(source_nums - nums),
                          extra_numbers=sorted(nums - source_nums)[:LIST_LIMIT],
                          extra_number_count=len(nums - source_nums),
                          alt_only_number_count=len(alts), alt_only_numbers=sorted(alts)[:LIST_LIMIT],
                          classification=classification, figure_reasons=reasons, flags=flags))
    issues = table_issues(text)
    nonfigure = [p for p in pages if p['classification'] != "figure"]
    low_count = sum(p['classification'] == "text loss" for p in nonfigure)
    severe = sum(min(p['word_coverage'], p['number_coverage']) < 0.50 for p in nonfigure)
    status = "BAD" if severe or low_count >= max(3, len(nonfigure) * 0.20) else "REVIEW" if low_count or issues or warnings or any(p['flags'] for p in pages) else "OK"
    mean = lambda items, key: sum(p[key] for p in items) / len(items) if items else None
    return dict(name=name, markdown=str(md_path.relative_to(ROOT)), pdf_pages=len(pdf_pages),
                markdown_pages=len(md_pages), warnings=warnings, pages=pages, table_issues=issues,
                summary=dict(pages=len(pdf_pages), mean_word_coverage=mean(pages, 'word_coverage'),
                             mean_number_coverage=mean(nonfigure, 'number_coverage'),
                             low_coverage_text_pages=low_count,
                             table_issue_counts={kind: sum(i['type'] == kind for i in issues) for kind in ISSUE_TYPES},
                             status=status))


def percent(value):
    return "—" if value is None else f"{value:.1%}"


def report_md(result: dict) -> str:
    summary = result['summary']
    lines = [f"# {result['name']} validation", "", f"Status: **{summary['status']}**. PDF pages: {result['pdf_pages']}; Markdown pages: {result['markdown_pages']}.",
             f"Mean word coverage: {percent(summary['mean_word_coverage'])}; mean number coverage (non-figure): {percent(summary['mean_number_coverage'])}.",
             f"Low-coverage text pages: {summary['low_coverage_text_pages']}. Table issues: {len(result['table_issues'])}.", "",
             "Coverage uses unique normalized token sets. Page numbers below are 1-based; Markdown markers are 0-based. Figure classification is heuristic. Extra numbers are possible OCR errors, not proof of hallucination.", ""]
    lines += [f"- {w}" for w in result['warnings']]
    lines += ["", "| Page | Words | Numbers | Classification | Alt-only numbers | Missing / extra | Flags |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
    for page in result['pages']:
        flags = "; ".join(page['flags'] + page['figure_reasons'])
        lines.append(f"| {page['page']} | {percent(page['word_coverage'])} | {percent(page['number_coverage'])} | {page['classification']} | {page['alt_only_number_count']} | {page['missing_number_count']} / {page['extra_number_count']} | {flags} |")
    lines += ["", "## Number differences", "", "Lists are sorted and capped at 40 per page; counts above are uncapped.", ""]
    for page in result['pages']:
        if page['missing_numbers'] or page['extra_numbers'] or page['alt_only_numbers']:
            lines += [f"### Page {page['page']}", "",
                      "Missing: " + (", ".join(page['missing_numbers']) or "none"), "",
                      "Extra: " + (", ".join(page['extra_numbers']) or "none"), "",
                      "Only in image alt text: " + (", ".join(page['alt_only_numbers']) or "none"), ""]
    lines += ["## Table issues", ""]
    for issue in result['table_issues']:
        row = issue['row'].replace("|", " / ").replace("\n", " ")
        lines.append(f"- Page {issue['page']}, line {issue['line']}: **{issue['type']}** — {issue['detail']}. Row: {html.escape(row)}")
    if not result['table_issues']:
        lines.append("None detected.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="PDF stems in the repository root")
    parser.add_argument("--all", action="store_true", help="all root PDFs with an output directory")
    parser.add_argument("--out", type=Path, default=ROOT / "reports/validation")
    args = parser.parse_args()
    names = set(args.names)
    if args.all:
        names.update(p.stem for p in ROOT.glob("*.pdf") if (ROOT / "output" / p.stem).is_dir())
    if not names:
        parser.error("specify names or --all")
    if any(Path(name).name != name or name in (".", "..") for name in names):
        parser.error("names must be PDF stems, without directory components")
    out = args.out.resolve()
    protected = (ROOT / "output").resolve()
    if out == protected or protected in out.parents:
        parser.error("--out must not be inside output/")
    out.mkdir(parents=True, exist_ok=True)
    results, errors = [], []
    for name in sorted(names):
        try:
            result = validate(name)
        except (OSError, ValueError, RuntimeError) as error:
            errors.append((name, str(error)))
            print(f"{name}: ERROR: {error}", file=sys.stderr)
            continue
        (out / f"{name}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        (out / f"{name}.md").write_text(report_md(result), encoding="utf-8")
        results.append(result)
        print(f"{name}: {result['summary']['status']} ({result['pdf_pages']} pages, {len(result['table_issues'])} table issues)", flush=True)
    lines = ["# Datasheet validation summary", "", "Means use unique normalized token sets; number means exclude figure pages.",
             f"Low coverage: words < {WORD_THRESHOLD:.0%} or numbers < {NUMBER_THRESHOLD:.0%} on non-figure pages.", "",
             "| Datasheet | Pages | Mean words | Mean numbers | Low text pages | Missing unit | Wrong column | Column shift | Ordering | Ragged | Status |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for result in results:
        s = result['summary']
        counts = " | ".join(str(s['table_issue_counts'][kind]) for kind in ISSUE_TYPES)
        lines.append(f"| [{result['name']}]({result['name']}.md) | {s['pages']} | {percent(s['mean_word_coverage'])} | {percent(s['mean_number_coverage'])} | {s['low_coverage_text_pages']} | {counts} | {s['status']} |")
    for name, error in errors:
        lines.append(f"| {name} | — | — | — | — | — | — | — | — | — | ERROR |")
        lines.append(f"\n{name}: {error}\n")
    (out / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
