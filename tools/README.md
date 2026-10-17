# Offline datasheet validator

Run from the repository root with the existing PyMuPDF virtual environment:

```sh
nice -n 10 ~/.venvs/pdf2llm/bin/python tools/validate.py --all
~/.venvs/pdf2llm/bin/python tools/validate.py ina190 tps6287b20 --out reports/validation
```

`--all` selects root PDFs with matching `output/<name>/` directories (15 in
this checkout). Names are PDF stems. Markdown lookup tries `<name>.md`, then
`markdown.md`, then a single `*.md`. Relative `--out` paths use the current
working directory; the default is the repository's `reports/validation`.
Nothing in `output/` is written. No API, network, or LLM is used. Dependencies
are Python's standard library and PyMuPDF. Poppler at `~/.local/bin/pdftotext`
is an optional fallback for pages with fewer than 30 extracted alphanumerics.

Each sheet gets Markdown and JSON reports; `SUMMARY.md` covers the selected
sheets. Output is sorted, has no timestamps, and is deterministic for the same
inputs and extraction versions. Per-sheet failures are printed, listed as
`ERROR` in the summary, and produce exit code 1; findings alone return 0.
Old reports for unselected sheets are retained, but are not in the new summary.

Coverage compares **sets of unique tokens**, not occurrence counts. Words are
alphabetic runs of at least three characters, case-insensitive. Numbers retain
sign and percent suffix, canonicalize decimal zeroes and explicit plus, and
expand `±x` into `-x` and `x`. Digits inside part/pin names count. Scientific
notation, number ranges, and locale-specific formatting are not semantically
interpreted. Normalization handles common LaTeX wrappers, subscripts,
superscripts, units, HTML tags/entities, Unicode minus signs, and whitespace.
Markdown images and their alt text are excluded from coverage; distinct numbers
found only in alt text are reported separately. Missing/extra/alt-only lists
are lexically sorted and capped at 40; total counts are uncapped.

Report pages are **1-based**; source markers `{N}----…` are 0-based. Source
Markdown line numbers are 1-based. Missing, duplicate, unmarked, and excess
Markdown pages are surfaced. A possible alignment issue is flagged when a
neighbor PDF page scores at least 65% and exceeds the current page's combined
word/number score by more than 18 percentage points (with at least 10 neighbor
word tokens). This is a heuristic, not an automatic reassignment.

Figure classification uses image-dominated Markdown or many isolated numeric
labels with six regular axis ticks; Markdown tables block these heuristics to
avoid treating specification tables as plots. Figure pages retain all metrics,
but are excluded from low-text counts and summary number means. Summary word
means include all pages. Empty token sets have coverage 100%, with empty PDF
extraction flagged for review. Image descriptions, diagrams, font extraction,
page footers, and package drawings can still cause misleading scores. Extra
numbers suggest possible OCR errors; they are not proof of hallucination.

Pipe tables and simple HTML tables (including row/column spans) are checked
when a header has MIN/TYP/MAX/NOM columns. Checks report missing units, units in
value columns or numbers in unit columns, condition text in value columns,
contradictory numeric ordering, and ragged rows. Blank continuation parameters
inherit units only within their parameter group. Legitimate supply-relative
expressions, reference dimensions, unit subscripts, and scale-only numeric
suffixes avoid shift warnings. Ordering compares plain numbers/percentages or
± intervals with matching suffixes; symbolic expressions, overlapping ±
intervals, and pairs of negative limits are not ordered. Complex/nested HTML,
multiline pipe rows, and semantic unit inference are outside scope. A single
row may generate multiple issue types.

Thresholds are constants near the top of `validate.py`: a non-figure page is
low coverage if words <85% **or** numbers <80%. Missing/alignment/extraction
flags also classify non-figure pages for review. Status is `BAD` if any
non-figure page has coverage below 50%, or low-text pages number at least
`max(3, 20% of non-figure pages)`; otherwise `REVIEW` for any table issue,
page/marker warning, or low-text page, and `OK` when none apply. These are
triage categories, not a statement that every flagged conversion is wrong.
