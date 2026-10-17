# Offline datasheet validator

Run from the repository root with stdlib and PyMuPDF only:

```sh
nice ~/.venvs/pdf2llm/bin/python tools/validate.py --all
~/.venvs/pdf2llm/bin/python -m unittest tools.test_validate
~/.venvs/pdf2llm/bin/python tools/test_validate.py
```

`--all` selects root PDFs with matching `output/<name>/` directories. Explicit
names and `--out <directory>` are supported. Markdown lookup tries `<name>.md`,
`markdown.md`, then a sole `*.md`. The default destination is
`reports/validation/`; writing inside `output/` is rejected. No network, API,
Datalab, or external extraction program is used. Reports contain no timestamps;
sheets, token lists, JSON keys and issues have stable ordering. Failures produce
exit code 1 and an ERROR summary row; findings alone return 0.

Coverage compares **unique normalized token sets**, not occurrences. Words
are alphabetic runs of three or more characters, case-insensitive. Numbers
retain sign, ignore trailing decimal zeroes and explicit plus,
and expand ± into signed endpoints. Coverage ignores the percent suffix because table values and percent-unit
cells are extracted in different reading orders. `numbers()` retains it for
table checks; coverage cannot diagnose an isolated lost percent sign. Digits in part and pin names count.
Normalization includes NFKC ligatures, soft hyphens and hyphenated line joins,
curly quotes, dotted leaders, spaced decimal points, HTML sub/sup tags, LaTeX wrappers and operators, and common Greek
symbols/names. Expressions, scientific notation, exponent semantics and locale
numbers are not evaluated. A low score remains evidence to inspect, not proof.

PDF filtering uses physical lines and word coordinates, in this order:

1. Remove lines touching the top/bottom 7% of page height (`MARGIN_FRACTION`).
2. Remove normalized lines recurring on at least 40% of document pages
   (`RECURRENCE_FRACTION`), after replacing each digit with `#`. At least three
   document pages are required. Count each signature once per page.
3. Remove explicit TI/ADI/LTC vendor URLs and feedback/copyright boilerplate,
   even when it falls outside the margins.
4. Assign individual words within image or clustered vector regions to figures.
   Vector boxes must exceed 35 by 30 points, and are padded 42 points horizontally
   and 28 vertically to include axis labels. Regions with at least two standard
   table labels, or at least three long horizontal and two long vertical rules with
   at least three prose lines,
   are preserved as tables. Lines of at least eight alphabetic words and Figure/Table
   captions remain text regardless of figure bounds. Images must exceed 900 square points.

Every page reports margin, recurring-line, explicit boilerplate and figure **occurrence** counts,
separately for words/numbers. Categories are exclusive. Text coverage excludes
these tokens; figure unique-token counts, region boxes, missing tokens and
alt-text coverage are separate JSON fields. Markdown image alt text never
fills text coverage. Alt-only numbers remain reported. A mixed figure/text page
can still have text loss. Pure figure pages have empty text denominators (100%).
The old Markdown/axis figure hints are informational, not exemptions from loss.
Blank extraction and missing/excess/duplicate markers are surfaced. Alignment
checks require at least 20 source words, a neighboring score ≥65%, at least ten
neighbor words and an advantage >18 percentage points (`ALIGNMENT_MARGIN`).

Pages in reports are 1-based; Markdown markers are 0-based, and Markdown line
numbers are 1-based. Missing words are sorted and capped at 30, number lists at
40; counts are uncapped. JSON also includes figure missing words/numbers.

Thresholds are explicit constants near the top of `validate.py`:

- Text loss: word coverage <90% **and** ≥8 missing unique words, **or** number
  coverage <90% **and** ≥3 missing unique numbers. Structural flags require inspection but do not count as measured text loss;
  pages without extractable PDF text are marked `unextractable`. Tiny denominators do not trigger loss from one or two misses.
- BAD: text-loss pages ≥max(3, 20% of all pages), or ≥8 distinct high-confidence
  table rows. Duplicate issue types on the same row count only once.
- REVIEW: any other loss, table issue, structural flag or marker warning.
- OK: none of those findings. This does not certify complete figure alt text.

Pipe and simple HTML tables (including row/column spans) are checked for missing
units, units/numbers in the wrong column, prose in numeric columns, contradictory
plain-numeric ordering, and ragged rows. Continuations inherit the first
parameter column's units; inline percentages are legitimate units. Timing rows
may share a printed unit across a table. Symbolic supply-relative limits and
scale suffixes are accepted. Negative magnitude limit pairs and overlapping ±
intervals are not ordered. Column-shift/wrong-column issues have `high`
confidence; missing units, ordering and ragged rows have `review` confidence.
Confidence is heuristic and is not PDF-grounded semantic verification.

Regression tests cover INA190 Gain error device selectors under MIN, valid
inline percentages, TPS22990 shared units, LTC2975 merged maximum/unit cells,
normalization, margin removal and table/figure separation. Complex nested HTML,
multiline pipe rows, dimensionless quantities and inferred units remain limits.

## Inspection and remaining misses

The requested INA190 pages 3, 5, 6 and 13–30 were inspected, along with LTC3313
application/plot pages and TPS63070/TPS22990 specification and figure pages.
Most initial losses were headers, copyrights, plot labels or normalization.
Low-count remnants include glued compounds (`commonmode`, `inpin`, `upto`),
variable fragments (`outmin`, `vref`), unit/word joins (`kohmto`, `ohmand`),
equation labels and dimensioned package-drawing text outside detected regions.
These should not be presented as confirmed prose omissions. Soft hyphen line
joins and clipped-word extraction artifacts were specifically corrected during
inspection. Margin and recurrence removal may also hide real repeated content;
figure boxes can miss detached labels or absorb adjacent prose. Counts and boxes
make that filtering auditable; empty filtered pages warrant checking the PDF.

The original table findings were reviewed across every sheet with findings.
TPS22990's 36 missing-unit reports were shared-unit false positives. Its page 5
shutdown-current rows really do place temperature conditions under MIN.
LTC2975 pages 6–7 are genuine: the full-temperature bullet consumes MIN, values
move right, and the maximum merges into UNITS (e.g. `1.44 V`, `200 μA`).
LTC3315A page 3 has the same maximum/unit merge. INA190 page 5 Gain error,
reference rejection and zero-output rows still place device selectors under
MIN; the Gain error regression remains detected. Inline percent cases in
TPS6287B20 and TS3A5018 no longer raise missing-unit/wrong-unit warnings.
AD5711R headroom/footroom ordering remains review confidence because numerical
ordering alone does not establish conversion loss.

Concrete inspected omissions and the per-datasheet table audit are recorded in
[`reports/validation/INSPECTION.md`](../reports/validation/INSPECTION.md).
The strongest prose/specification losses were LT1965FB p4 (missing voltage
maxima), TS3A5018 p8 (missing test conditions), and missing figure captions on
AD5711R/AD5710R p27 and TPS6287B20 p55. Six other concrete omissions listed there
are package/land-pattern dimensions absent even from alt text. They should be
reviewed as drawing information losses rather than ten confirmed prose losses.
