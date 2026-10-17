# Review log: critical tables of priority datasheets

Scope (1-based PDF pages): ina190 p3-p6, ltc3313 p2-p4 + p9, ltc3315a p2-p4 + p10,
ltc3309a p2-p4 + p9. Sections: Absolute Maximum Ratings, Recommended Operating
Conditions, ESD/Thermal, Electrical Characteristics, Pin configuration / Pin
functions, Order information. These parts have no register maps.

Method
1. Pages rendered with `tools/review/render_pages.py` (200 dpi page + 300 dpi top/bottom crops).
2. Each page independently reviewed by **agy** (`gemini-4-argon-high`) and **grok**
   with `tools/review/review_prompt.tmpl` (image = ground truth, JSON output).
   Raw results: `reports/review/llm/{agy,grok}/<name>_p<N>.json`; after-fix re-review: `reports/review/llm_after_fix/`.
3. Every reported discrepancy was checked by hand against the PDF text layer
   (PyMuPDF text, `tools/review/rowcheck.py` word x-coordinates vs MIN/TYP/MAX/UNIT
   header positions) and/or the rendered image. Only confirmed items were fixed.
4. Fixes are recorded as exact old/new text with evidence in `reports/review/fixes.json`
   and applied with `tools/apply_md_fixes.py` (only `output/<name>/<name>.md`; html/json/chunks untouched).
5. Fixed pages were re-rendered from the corrected md and re-reviewed by both models
   (results below), and `tools/validate.py` geometry check was rerun (0 mismatches on the 4 sheets).

## Per-page status

| Datasheet | Page | Sections | agy (before) | grok (before) | Decision | Fix ids | Re-review after fix |
|---|---|---|---|---|---|---|---|
| ina190 | 3 | Pin configuration, Pin functions | 0 | 0 | verified OK | - | - |
| ina190 | 4 | Abs Max, ESD, Recommended, Thermal | 8 | 7 | confirmed (image + text) | ina190-p4-absmax-analog-inputs, ina190-p4-absmax-ref-out-unit, ina190-p4-esd-columns | agy 0, grok 0 |
| ina190 | 5 | Electrical Characteristics | 3 | 0 (missed) | confirmed (image; also validator column-shift) | ina190-p5-ec-gain-error-subconditions, -rvrr-, -vzl- | agy 0, grok 0 |
| ina190 | 6 | Electrical Characteristics (cont.) | 0 | 0 | verified OK | - | - |
| ltc3313 | 2 | Abs Max, Pin configuration, Order info | 3 | 2 | confirmed (PDF text, Pin Functions p9) | ltc3313-p2-pinout-alt, -pinout-text, -pinout-caption | agy 0, grok 0 |
| ltc3313 | 3 | Electrical Characteristics | 0 | 0 | verified OK | - | - |
| ltc3313 | 4 | Electrical Characteristics (cont.), Notes | 0 | 0 | verified OK | - | - |
| ltc3313 | 9 | Pin functions | 0 | 0 | verified OK | - | - |
| ltc3315a | 2 | Abs Max, Pin configuration (LQFN, WLCSP) | 1 | 1 | confirmed (PDF text, Pin Functions p10) | ltc3315a-p2-wlcsp-ball-map | agy 0, grok 0 |
| ltc3315a | 3 | Order info, Electrical Characteristics | 4 | 4 | confirmed (word geometry) | ltc3315a-p3-ec-pmos-current-limit | agy 0, grok 0 |
| ltc3315a | 4 | Electrical Characteristics (cont.) | 5 | 4 (1st run) / 3 (2nd run) | 4 rows confirmed (word geometry); "Minimum On Time ● in MIN" kept (values already in correct TYP/MAX columns, ● is the full-temp marker) | ltc3315a-p4-ec-max-duty-cycle, -pgood-delay, -pgood-pulldown, -no-clock-detect, -header-power, -header-oscillator | agy 0, grok 0 |
| ltc3315a | 10 | Pin functions | 0 | 0 | verified OK | - | - |
| ltc3309a | 2 | Abs Max, Pin configuration, Order info | 4 | 9 | confirmed (PDF text, Pin Functions p9) | ltc3309a-p2-pinout-alt, -pinout-text, -pinout-caption, -order-extra-row, -order-automotive-header | agy 0, grok 0 |
| ltc3309a | 3 | Electrical Characteristics | 0 | 0 | verified OK | - | - |
| ltc3309a | 4 | Electrical Characteristics (cont.) | 0 | 0 | verified OK | - | - |
| ltc3309a | 9 | Pin functions | 0 | 0 | verified OK | - | - |

"verified OK" = both models found no discrepancy in the critical tables of that page and
`tools/validate.py` found no table/geometry issue there. It is a strong signal, not a
certificate: the geometry check could only match part of the rows (see SUMMARY.md
"unverifiable"), and grok missed the ina190 p5 issue that agy and the validator caught.

## Errors found and fixed (22 fixes, see fixes.json for exact text)

High severity (would mislead an LLM reading the spec):
- ina190 p4 Abs Max: analog-input rows shifted; md read "Differential ... MAX –42" and lost
  "MIN GND – 0.3" for VIN+/VIN– to GND. PDF: Differential –42 / 42 V; to GND GND – 0.3 / 42 V.
- ina190 p4 ESD: ±3000 / ±1000 under the UNIT header, unit V missing.
- ltc3315a p3: PMOS current limit md "– | 2.9 | 3.2 | 3.5 A" -> PDF MIN 2.9 / TYP 3.2 / MAX 3.5 A.
- ltc3315a p4: Maximum Duty Cycle 100 was TYP (PDF MIN); PGOOD Delay 120 was MIN (PDF TYP);
  PGOOD pull-down 10/20 were MIN/TYP (PDF TYP/MAX); no-clock-detect 10 was MIN (PDF TYP).
- ltc3315a p2: WLCSP ball map described as "Pin 1..16" instead of balls A1..D4.
- ltc3309a p2: pin diagram text/alt said pin 11 PGND, pin 12 AGND, pin 5 PGND (PDF: PGOOD, FB, SW).
- ltc3313 p2: pin diagram text lost pin numbers/names (pins 15-18 RT/SSTT/ITH/FB).
Medium / low:
- ina190 p4 REF/OUT unit V missing; ina190 p5 device sub-conditions (A1 devices...) in MIN column.
- ltc3315a p4 headerless EC sub-tables (header added); ltc3309a p2 spurious empty order row,
  empty automotive header; ltc3309a θJA/θJB/ΨJT mislabeled in generated alt text; "PGGOOD" typo (ltc3313).

## Not fixed / open
- html/json/chunks outputs still contain the original Datalab errors (only .md was corrected).
- ltc3315a p4 "Minimum On Time": ● marker sits alone in MIN (no MIN value) - left as is.
- LTC tables mix "● 2.25" (marker inside MIN cell) with a separate ● column in sub-tables;
  consistent but not uniform.

## Batch 2 (EC tables flagged by the geometry check)

Scope (1-based PDF pages): lt1965fb p4, ltc2975 p5-p10, tps6287b20 p6/p7/p10,
ts3a5018 p4/p5/p8, sn74avc4t774 p6/p7, tps22990 p5, tps63802 p6.

Method: same as batch 1, plus `tools/review/realign.py`, which rebuilds each md
row from PDF word geometry (rows aligned in order by their numbers, LTC
full-temperature marker detected) and proposes the corrected cells. A fix was
applied only when realign/word geometry agreed with agy and/or grok, or when I
checked the PDF words/pdftotext by hand (noted as pdf-text/pdf-word-geometry in
`fixes.json` `sources`). Raw pre-fix reviews: `reports/review/llm_batch2/`.
Post-fix reviews: `reports/review/llm_batch2_after_fix/`.

| Datasheet | Page | Problem (Datalab) | Evidence | Fix ids (prefix) | Rows |
|---|---|---|---|---|---|
| lt1965fb | 4 | ● merged into MIN, MAX lost (Regulated Output, ADJ); ● on rows without it; ADJ/Line Regulation labels shifted; Dropout H-grade row dropped | realign + agy + visual + pdftotext | `lt1965fb-p4-` | 15 |
| ltc2975 | 5, 6, 7, 9 | "\| ● \| a \| b \|": ● put in MIN, values shifted, MAX/TYP lost, units merged | realign + agy (all) + grok (p5, p6) | `ltc2975-p5..p9-L*-geometry` | 44 |
| ltc2975 | 10 | t_OFF_MIN 100 ms in MIN (headerless table); Note 10 V_I0 | words (100@TYP), agy; grok + pdftotext | `ltc2975-p10-` | 2 |
| ltc2975 | 6-8 | absolute-value bars lost in conditions | agy + pdftotext | `ltc2975-p*-abs-bars-` | 16 |
| ltc2975 | 7 | channel subscript n rendered as _H | agy + pdftotext | `ltc2975-p7-subscript-n-` | 8 |
| ltc2975 | 8 | (none: ● sits at end of CONDITIONS; only cosmetic notes) | agy | - | 0 |
| tps6287b20 | 10 | TI shift: values in MIN, MAX lost (R_DS(ON), t_on, t_off, I_SW...) | realign + agy + grok | `tps6287b20-p10-` | 14 |
| tps6287b20 | 7 | SUPPLY table lost description column: I_Q/I_SD conditions in MIN, MAX in UNIT | agy + grok + words | `tps6287b20-p7-supply-table-columns` | 11 |
| ts3a5018 | 4 | Abs Max lacked conditions column (I_K/I_IK -50 in UNIT, 0-7 V condition lost); ESD value in UNIT; R_θJA shifted one package | agy + words | `ts3a5018-p4-` | 3 tables |
| ts3a5018 | 8 | TEST CONDITIONS column lost in 3 tables; 25°C/Full tags wrong | agy + grok + words | `ts3a5018-p8-` | 3 tables |
| tps22990 | 5 | I_SD,VIN: V_IN sub-condition in T_A column, T_A in MIN | agy + words | `tps22990-p5-isd-vin-columns` | 12 |
| tps63802 | 6 | R_DS(ON): second condition fragment in MIN | words | `tps63802-p6-rdson-conditions` | 4 |
| sn74avc4t774 | 6, 7 | false positives (VCCA/VCCB matched Abs Max row; IOH/IOL matched the row holding the centred label) | agy 0, grok 0, words | validator fix | 0 |
| tps22990 | 6 | false positives (R_ON 105°C rows matched a row of the next table) | words | validator fix | 0 |
| ad5711r | 5 | Headroom 70/50, Footroom 250/120 (MIN > TYP) | words: the PDF prints exactly that | faithful, left as is | 0 |
| tps6287b20 / ts3a5018 | 6 / 5 | realign proposals were cosmetic (footnote, units); agy 0 | agy | - | 0 |

Validator changes driven by this batch (tests in `tools/test_validate.py`):
explicit ambiguity, value fallback abstains when values recur in another table,
numeric-range cells as row anchors, band word ownership, codex advisory review
items (whole-word Conditions/Comments header, MIN+MAX for Title-case headers,
formula skip needs an operator and whole-token numbers), and an `out_of_scope`
count for rows of non-spec tables.

### Batch 2 after-fix re-review

Fixed pages re-rendered from the corrected md (`~/work/pdf2llm-run6`) and reviewed again:
lt1965fb p4, ltc2975 p5-p10, tps6287b20 p7/p10, ts3a5018 p4/p8, tps22990 p5, tps63802 p6 (13 pages).

- **agy:** 13/13 pages with 0 high/medium discrepancies. Only low: the ltc2975 p10 t_TIMEOUT_BUS ● sits in MIN, which is the repo convention (● alone in MIN when the row has no MIN value; the values are 25/35 ms TYP/MAX, as the PDF words confirm).
- **codex** (now allowed without sandbox, images passed with `-i`): 13/13 with 0 high. One medium on ltc2975 p7 I_IIN is a false positive (pdftotext: `VIIN_SNSP = VIIN_SNSM = VIIN_SNS`, matching the md). The p6/p8 symbol-name lows were fixed (`ltc2975-p6-symbol-*`, `ltc2975-p8-symbol-vout-en-*`).
- **grok:** 13/13 done; 0 new real errors (see batch 3 note).

Earlier rounds (run4/run5) found the absolute-value bars, the _H subscripts and the V_FS_VDAC shared condition, which are now fixed.
`fixes.json` replays exactly: applying it to the original Datalab md (commit 6439792) reproduces every corrected file byte for byte.
Raw outputs: `reports/review/llm_batch2_after_fix/{agy,codex,grok}/`.

### Batch 3: spec pages no LLM had reviewed

Inventory: every EC / Abs Max / Recommended / switching page of the 15 converted datasheets that had no earlier review (37 pages: ad5593r p3-7, ad5711r p4-11, lt1965fb p2/p5, ltc2975 p2/p4, max31730 p2-4, tps22990 p4/6-8, tps6287b20 p8/9/11/12, tps63070 p4-7, tps63802 p5/7, ts3a5018 p6/7/9), plus sn74avc4t774 p8-11 (switching tables, found by a coverage scan). agy and codex reviewed all 41 pages. grok was slower and covered a subset (see below).

| Datasheet | Page | Problem (Datalab) | Evidence | Fix ids (prefix) | Rows |
|---|---|---|---|---|---|
| sn74avc4t774 | 8 | TA = 25°C group: TYP/MAX values put in MIN/TYP (I_I, I_off ×2, I_OZ) | codex + agy + words (x-centres under TYP/MAX) | `sn74avc4t774-p8-25C-typ-max-shift-` | 4 |
| ad5711r | 8 | 65 µA continuation row (IDAC-to-IDAC DAC-to-DAC, from p7) merged into the VDAC-to-IDAC Analog row; the header condition was glued to it | codex + agy + words | `ad5711r-p8-65uA-continuation-row` | 3 |
| ad5593r | 3 | f_IN = 10 kHz condition belongs to the ADC PERFORMANCE header row, not to Resolution | agy + codex + words | `ad5593r-p3-fin-on-adc-header` | 2 |
| ltc2975 | 2 and text | MFR WATCHDOG_T → MFR_WATCHDOG_T (8 lines, including "WATCH DOG") | agy + codex + pdftotext (13×, never with a space) | `ltc2975-mfr-watchdog-` | 8 |
| tps6287b20 | 9 | EC condition prints CONTROL2:SYNCH_OUT_PHASE (a PDF typo, kept as printed) | agy + codex + pdftotext | `tps6287b20-p9-synch-out-phase-` | 2 |
| lt1965fb | 5 | Note 3: T_J ≅ T_A (Symbol 0x40), md had ≡ | codex + glyph/crop | `lt1965fb-p5-note3-cong` | 1 |
| lt1965fb, max31730 | 2, 5 / 3 | overbars on SHDN/THERM dropped | codex | not changed: Datalab drops overbars throughout; repo-wide convention decision | 0 |
| ad5711r | 7 | PDF prints "ixternal reference" (131 nV/√Hz); md says internal | words | left as is (the ext/ext/int/int pattern implies internal); flagged | 0 |
| ad5711r | 10 | Figure 4 LDAC timing prose descriptions (codex) | codex only | figure description, not a spec; not changed | 0 |

All other pages: 0 high/medium findings from both agy and codex.
After-fix re-review (agy + codex, `~/work/pdf2llm-run9`) of ad5593r p3, ad5711r p8, sn74avc4t774 p8, tps6287b20 p9 and lt1965fb p5 found 0 discrepancies.
grok after-fix batch 2 (13 pages) is complete. The only remaining items are stale findings from a pre-fix snapshot (ltc2975 p8 V_VOUT_ENn, already fixed) and one layout note (tps22990 p5: a shared V_ON/V_OUT condition written on the first row only).

Validator changes in this batch: unverifiable reasons are recorded. Repeated sub-rows are resolved by row order: an md row that follows an anchored row takes the next PDF band, but only when that band is among the tied candidates. Each md row picks its PDF table from its own values (the Abs Max and Recommended tables share labels). Identical value rows in two tables are accepted.
Totals: verified 1059 → 1300, mismatched 0 → 0, unverifiable 393 → 152.
Most of the remaining unverifiable rows are outside spec tables: scope-readout tables on the tps22990 p13/14 plots, and the tps6287b20 / tps63070 design-example "VALUE" tables.
Known gap: TI tables with two MIN/TYP/MAX groups (TA = 25°C and full range, e.g. sn74avc4t774 p8) are out of validator scope. The p8 shift above was found by the LLMs, not by geometry.
Raw outputs: `reports/review/llm_batch3/` and `reports/review/llm_batch3_after_fix/`.
