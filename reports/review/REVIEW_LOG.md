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
