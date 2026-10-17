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

## Geometry column verification

`geometry.py` adds a separate PDF-grounded check; the existing coverage and
header-based checks keep their thresholds and behavior. It reads page words
with `get_text("words")`, groups uppercase MIN/TYP/NOM/MAX/VALUE/UNIT(S)
headers by baseline, and places column boundaries halfway between their centers.
The first value interval extends half a column to the left; the last extends to
the page edge. Repeated headers delimit separate schemas. Empty/headerless
continuations reuse the page schema or the previous Markdown table's schema,
with value columns aligned to the right. An unrelated named header (including a
thermal metric table) prevents inheritance.

Numeric PDF baselines collect nearby words within four points. Row matching uses
fuzzy parameter/condition token recall within five points, with weaker support
from shared labels within 30 points. The most specific condition must match at
least 95%, including every numeric condition token. Device selectors can anchor
rows with vertically centered parent parameters. Competing matches within a
0.035 score margin, or repeated conditions on adjacent baselines, are
unverifiable. Numeric value agreement does not select the PDF row. This avoids
matching a corrupt value to a convenient different row.

Matched numeric occurrences are compared by their x-center columns, preserving
sign and ± and canonicalizing decimal precision. Supply-relative expressions
such as `GND – 0.3` and `V_IN – 0.1` retain their numeric tokens. Missing PDF
values and misplaced condition prose are also reported. Printed units are
compared after typography normalization; blank shared units are allowed. A
multi-baseline Markdown cell is conservatively unverifiable when it cannot be
compared to one PDF baseline. Duplicate numeric limits require separate
occurrences. Complex wrapped values, side-by-side schemas, missing PDF text,
and ambiguous/short row labels can remain unverifiable; this is not complete
semantic verification of expressions, exponents, or diagrams.

JSON issues include `page`, `line`/`md_line`, `parameter`, `value`, `md_column`,
`pdf_column`, and `confidence`. Types are `geometry column mismatch` and
`geometry missing value`; both have high confidence and join the existing
REVIEW/BAD row thresholds. JSON `summary.geometry_rows`, each sheet report,
and SUMMARY.md distinguish verified OK, mismatched and unverifiable numeric
Markdown rows. Multiple findings on a row count once in these row totals.

Regression fixtures freeze the broken LTC3315A and INA190 rows independently of
future Markdown repairs. Correct controls and false-positive samples read the
current `output/` files. The geometry checks require only stdlib and PyMuPDF,
make no API calls, and produce deterministic reports.

### Geometry matching extensions (batch 2)

- **Value fallback** (`match_by_values`): when prose matching cannot pick a PDF row,
  the md row is matched by its numeric values (they must be a sub-multiset of exactly
  one PDF row; a single value also needs prose overlap nearby). Column placement is not
  used to choose the row, so shifted/missing values are still reported. Counted as
  `value_matched` in the JSON stats.
- **ADI layout**: Title-case `Min Typ Max Unit` headers are accepted when at least three
  labels share a line, and a `Test Conditions/Comments` column to the right of `Unit`
  bounds the unit column and is treated as prose.
- Formula cells (e.g. `20 + 0.1CB`) are not reported missing when their numbers appear
  elsewhere in the md row; unit cells such as `LSB12` keep their digits when compared.

## Geometry matching extensions (batch 3)

- Ambiguity is now explicit: when a row's prose matches several rows of its own
  table, a clear hit in another table (e.g. Abs Max "Supply voltage" vs the
  Recommended row) is discarded instead of reported as a mismatch.
- The value fallback abstains when the row's values occur in several bands of
  any table on the page (tps22990 R_ON temperature sub-rows).
- Numeric range cells ("1.1V to 1.3V") are prose queries, so a sub-row is not
  matched to the row that carries the vertically centred parameter label.
- Prose words belong only to their nearest band, so packed rows do not borrow
  a neighbour's condition.
