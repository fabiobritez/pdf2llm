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

### Run12: prose / register / application pages (codex + grok)

Scope: 138 pages rendered in `~/work/pdf2llm-run12` (functional description, register/command, applications pages) with `tools/review/review_struct.tmpl`.
codex (`gpt-6.1-sol`, `xhigh`, confirmed in each output header) reviewed all 138 pages. 32 pages first had only a grok review because codex hit its usage limit (run12b: ltc3309a p6/8/22/23, ltc3313 p11-20, ltc3315a p12-14, tps63070 p9, tps63802 p9/10/13-17, ts3a5018 p17/18; run12c: ltc3315a p15-19). codex re-ran them on 2026-10-17 at 20:12 UTC; ltc3313 p14 and ts3a5018 p17 were re-run at 21:0x UTC. Each run used about 11-14k tokens, the same as the earlier codex batch.

| Datasheet | Page | Finding | Evidence | Fix ids | Decision |
|---|---|---|---|---|---|
| ltc3315a | 16 | Table 1 (×2) and Table 2: md "Würth", PDF prints "Wurth" | codex + grok-4.7 (crops) + PDF words (U+0075) + image; validator listed "wurth" as missing | `ltc3315a-p16-table*-wurth-as-printed` | fixed (as printed) |
| ltc3313 | 14 | Table 2: md "Würth", PDF prints "Wurth" | codex + grok-4.7 + PDF words + image | `ltc3313-p14-table2-wurth-as-printed` | fixed (as printed) |
| ltc3313 / ltc3315a / tps63802 | 17 / 13 / 15 | LTpowerCAD, Overtemperature heading, "continuos"/"power safe mode" as printed | grok + codex + PDF text | already in 0deb33e | - |
| ltc3309a | 6 | 27 curve-value findings (G10-G18) | codex (grok: 4) | tables removed in 7ecef66 (`ltc3309a-p6-*-figure-curve-table-removed`) | obsolete |

All other pages in the 32-page set: 0 codex findings.
ltc2975 p63: fresh codex and grok-4.7 reviews of the current md (`~/work/pdf2llm-run13`) found 0 discrepancies, matching the run10 reviews. A PyMuPDF word diff of md vs PDF also found no differences apart from the running header/footer and bullet glyphs. Checked against the image: table row/column assignment, `Mfr_retry_count [2:0]`, "0: No retries:" and the truncated `Mfr_track_en_chann`, all kept as printed.

### ina190 full page-by-page review (2026-10-26)

Scope: all 47 PDF pages of `ina190.pdf`. For each page: rendered image (110-150 dpi), `pdftotext -layout`, PyMuPDF spans (sub/superscripts) and word rows, all compared with the `{N-1}` section of `output/ina190/ina190.md`. Tables on p31, p32, p34, p35, p36 and p37 (orderable parts, tape-and-reel, box dimensions) were compared row by row against PDF word rows, and all 110 rows match. The EC, Abs Max, ESD, Recommended and Thermal tables (p4-p6) match the PDF values and columns cell by cell.
109 new fixes, all `ina190-p*` ids in `fixes.json` (105 low, 4 medium). `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 6 | EC (continued): CONDITIONS header was over the parameter-name column; the real conditions column had no header | `ina190-p6-ec-conditions-header-column` | medium |
| 7-12 | Figure sub-labels printed under each plot (`A1 devices`, `VS = 5.0 V, A3 devices`, `VENABLE = 0 V`, ...) were missing from the body. Figures 5 and 6 (both "Gain Error Production Distribution") could not be told apart | `ina190-p7-fig5-fig6-device-labels`, `ina190-p*-fig*-sublabel` | medium / low |
| 38, 41 | DCK0006A / RSW0010A outline descriptions: min/max pairs given as "X (Y reference)", RSW described as 8 pins and square, package called "SOT-116", wrong dimension meanings | `ina190-p38-dck-*`, `ina190-p41-rsw-*` | medium / low |
| 1, 13, 16-20, 22, 24, 27-29 | AI circuit descriptions contradicted the drawings: IN+/IN- swapped (Fig 35), REF tied to the output or a supply (Fig 1, 36, 37, 39), C_BYPASS "connected to ENABLE" (Fig 42, 43), wrong block diagram topology (Fig 13 page), feedback vs series filter resistors (Fig 40, 46-48), GPIO/ADC wiring (Fig 38) | `ina190-p*-fig*`, `ina190-p13-block-diagram-topology`, `ina190-p1-typical-application-*` | low |
| 7-12 | Curve descriptions with wrong statements: Fig 6 is a histogram, not a line graph; Fig 7 centre; Fig 14/15 level; Fig 20 roll-off frequency; Fig 25 invented 12 V step; Fig 29 IBN decreases; Fig 31-33 ordering | `ina190-p7-figs1-6-*`, `ina190-p8-fig7-*`, `ina190-p9-*`, `ina190-p10-fig20-*`, `ina190-p11-*`, `ina190-p12-*` | low |
| 39, 40, 42, 43, 45, 46 | Land-pattern/stencil descriptions: pad length/width/pitch confused, pin positions wrong, "4x4 grid", solder-mask labels swapped | `ina190-p39-*` ... `ina190-p46-*` | low |
| 1, 3, 20 | As printed: SC70 body size `2.00 mm x 1.25 mm` (letter x); `VS` without subscript in three Pin Functions cells; `connections.If` (no space) | `ina190-p1-device-info-sc70-x-as-printed`, `ina190-p3-*`, `ina190-p20-kelvin-connections-if-as-printed` | low |
| 2 | Revision history: page numbers 1, 1, 22, 22, 24 were missing | `ina190-p2-revhist-page-numbers` | low |
| 14 | Equation (1) number was written as a fifth list item | `ina190-p14-eq1-number-not-bullet` | low |
| 28 | Fig 47 label list: R_F three times (PDF: twice) and the stray IN+ label was missing | `ina190-p28-fig47-labels-rf-count` | low |
| 38, 41, 44, 45 | Drawing title block / `SCALE n` lines missing | `ina190-p38-dck-outline-header`, `ina190-p41-rsw-scale`, `ina190-p44-ddf-scale`, `ina190-p45-ddf-board-layout-header` | low |

No error found on p4, p5, p15, p21, p23, p25, p26, p30-p37 or p47. The earlier p4/p5 fixes still hold.
After the fixes: `validate.py --all` reports ina190 OK (word/number coverage 94.6/93.4% → 94.8/94.0%; p38 and p45 now 100%). `check_llm_fidelity.py`: ina190 has 0 spec-table failures and the source numeric subset is True; the only extra token is the pre-existing `271` from the slua271 link. `relocate_images.py --check ina190`: OK. `check_struct_tables.py`: unchanged (ok 4, loose 5). `unittest` test_validate / test_llm_compact / test_struct_tables: OK.
`ina190.llm.md` was regenerated with `tools/llm_compact.py ina190`. Every summary claim was checked against the md. One citation was corrected: the bidirectional REF bullet now cites [p16, p18] (bidirectional mode is on p18) in `reports/llm/summaries/ina190.md`.

Not changed / open:
- Dash and micro-sign typography: the PDF prints `IN–`, `–3`, `IB–` with an en dash and uses `µ`; Datalab wrote hyphens and sometimes `μ`. This is repo-wide normalization, so it was left as is.
- Running headers and footers are omitted, following the convention for all datasheets: `SBOS863D – ...`, the p1 "An IMPORTANT NOTICE at the end..." footer, `Addendum-Page n`, and the repeated "IMPORTANT NOTICE" header on p47.
- p33 `Disclaimer:The` (no space in the PDF) is kept as `**Disclaimer:** The`, because removing the space would break the bold markup.
- Structure-only oddities were left: `###### Page` / `### Page` headings in the revision history, the p23 equation (5) number inline after the last bullet, `# DDF0008A` as H1 on p44, and the p28 figure-label dump (other figures have none).
- p29 Fig 48: it is ambiguous whether the REF trace or only the GND trace reaches the ground via in the drawing. The description was not changed there.
- Figure descriptions remain AI text. They now agree with the drawings on connections and dimension meanings, but approximate curve levels (for example "about 25 nV/√Hz") are still estimates. Read values from the image/PDF.

### lt1965fb full page-by-page review (2026-10-26)

Scope: all 22 PDF pages of `lt1965fb.pdf`. For each page: rendered image (`tools/review/render_pages.py`), `pdftotext -layout`, and PyMuPDF word rows (x positions under MIN/TYP/MAX/UNITS, ● positions, spans for sub/superscripts) were compared with the `{N-1}` section of `output/lt1965fb/lt1965fb.md`. The EC tables (p4, p5) match the PDF cell by cell, including where ● is present or absent: H-grade rows have no ●, as printed. Abs Max (p2), the order tables (p2, p3), the thermal tables (p15) and Related Parts (p22) were checked row by row.
82 new fixes, all `lt1965fb-p*` ids in `fixes.json` (5 medium, 77 low). Description fixes have two entries each (`-alt` for the image alt text, `-desc` for the repeated paragraph). `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 1 | Title block 'LT1965 Series / 1.1A, Low Noise, Low Dropout Linear Regulator' was missing; the md started at FEATURES | `lt1965fb-p1-title-missing` | medium |
| 3 | Part marking for LT1965EMS8E-3.3 / LT1965IMS8E-3.3: md had LDMD (the DFN marking); the PDF prints LTDMF | `lt1965fb-p3-ms8e-3.3-marking-*` | medium |
| 18 | MS8E dimension lists were AI guesses: wrong meanings, 0.53 ±0.152 repeated in four views, and 1.68 ±0.102, 3.20 – 3.45, 4.90 ±0.152, 3.00 (NOTE 4), 0.18, 0.22 – 0.38, 0.1016 ±0.0508 missing. Replaced by the printed labels grouped by view | `lt1965fb-p18-ms8e-dimension-lists` | medium |
| 20 | TO-220 dimension names wrong for most labels (.460 – .500 vs .330 – .370, .230 – .270, .135 – .165, ...). Values unchanged | `lt1965fb-p20-to220-dimension-meanings` | medium |
| 1, 8, 11-13, 16, 17, 22 | Drawing numbers missing: 1965 TA01, G19-G26, F01-F06, TA03, TA04, plus `(DD8) DFN 0509 REV C` and 'BOTTOM VIEW—EXPOSED PAD' (p6/p7 G numbers were already present) | `*-drawing-number`, `lt1965fb-p17-dd8-drawing-id` | low |
| 7, 8, 10 | Curve descriptions: G15-G18 load labels lacked the printed asterisks; G14 is the adjustable LT1965, not 'the general family'; G23/G24 have no peak at 2V; G25 is not linear and starts below 1mA; G35 '0.5P-P'; G37 had an invented load-current dependence and was missing its printed conditions; G38 µV/√Hz and LT1965-1.5 curve; G41 load step timing; G42 'Soft Start' and SHDN step time | `lt1965fb-p7-*`, `lt1965fb-p8-g2*-desc*`, `lt1965fb-p10-*` | low |
| 11, 12, 17, 22 | Circuit descriptions contradicted the drawings: Fig 1 SENSE path (Kelvin connection) and GND return; Fig 2 output capacitor; the paralleling circuit (R1/R2 are input sense resistors, R6/R7 the ADJ divider, C2 the output capacitor, C3 op-amp feedback); TA04 was missing C2 and VIN > 2.7V | `lt1965fb-p11-fig1-desc*`, `lt1965fb-p12-fig2-desc*`, `lt1965fb-p17-ta03-paralleling-desc*`, `lt1965fb-p22-ta04-desc*` | low |
| 13, 17, 19 | Figure 4 Y5V end point; DD8 and DD5 package descriptions had wrong dimension meanings and misprinted mm tolerances (`+.0305`, `+.0203`, `±.0305`; PDF: +0.305, +0.203, ±0.305), and the thick-paste pad layout had labels taken from DETAIL A | `lt1965fb-p13-fig4-*`, `lt1965fb-p17-dd8-desc*`, `lt1965fb-p19-dd5-*` | low |
| 11, 12, 16, 17, 18, 22 | Typography as printed: R_P (capital P), Fig 2 equation R2/R1 not subscripted, DD8 Note 1 `M0-229` (digit zero), MS8E notes inch marks `(.006")`, curly “A” in Related Parts. A sentence split across the p16 columns ('9V clamp / voltage') was rejoined | `lt1965fb-p11-sense-rp-subscript`, `lt1965fb-p12-fig2-eq-*`, `lt1965fb-p17-dd8-note1-*`, `lt1965fb-p18-ms8e-notes-*`, `lt1965fb-p22-related-*`, `lt1965fb-p16-adj-clamp-*` | low |

No error found on p2, p4, p5, p6, p9, p14, p15 or p21. The earlier p4/p5 fixes still hold.
After the fixes: `validate.py --all` reports lt1965fb OK, with word/number coverage going from 99.5/99.2% to 99.9/100.0% and geometry 63 / 0 / 0. `check_llm_fidelity.py`: lt1965fb has 0 spec-table failures and the numeric subset is True. `relocate_images.py --check lt1965fb`: OK. `check_struct_tables.py`: unchanged. `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).
`lt1965fb.llm.md` was regenerated with `tools/llm_compact.py lt1965fb`. Every summary claim in `reports/llm/summaries/lt1965fb.md` was re-checked against the corrected md (p1, p2, p4, p5, p11, p12); none needed a change.

Not changed / open:
- p1 trademark line `LT, LT, LTC, LTM, ...`: the first item is the Linear logo glyph in the PDF, which Datalab rendered as 'LT'. Left as is.
- Repo-wide conventions were kept: hyphen for the en dash (–40°C), Greek μ next to µ, SHDN overbars dropped in headings and tables, and running headers/footers omitted, including the p21 'Information furnished by Linear Technology…' disclaimer and the p22 address/copyright footer (other LTC sheets omit them too).
- Structure-only oddities: `## LT1965 Series` running-header headings, `## Thermal Considerations` at H2 while sibling subsections are H3, `###### **NOTE:**` on p17.
- Figure descriptions are still AI text. They now agree with the drawings on connections, labels and dimension meanings, but approximate curve levels (for example Fig 6 "approximately 5.5mA at 9V", G29 "minimum around 75°C") are estimates. Read values from the image/PDF.

### ltc3309a full page-by-page review (2026-10-26)

Scope: all 26 PDF pages of `ltc3309a.pdf`. For each page: rendered image (`tools/review/render_pages.py`, plus 220-300 dpi crops of schematics, the block diagram and the rotated p24 package drawing), `pdftotext -layout`, PyMuPDF word rows and spans (sub/superscripts, glyphs), and a word-level diff of the PDF text against the `{N-1}` section of `output/ltc3309a/ltc3309a.md`. The EC table (p3) matches the PDF cell by cell, including the ● column and MIN/TYP/MAX positions. Table 1 (p14), Table 2 (p15, 23 rows), Table 3 (p16), the order tables (p2), the package dimensions (p24), Revision History (p25) and Related Parts (p26) were checked row by row.
109 new fixes, all `ltc3309a-p*` ids in `fixes.json` (2 medium, 107 low). Description fixes have two entries each (`-alt` for the image alt text, `-desc` for the repeated paragraph). `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 1 | Part number title 'LTC3309A' was missing; the md started at the subtitle | `ltc3309a-p1-title-missing` | medium |
| 10 | Block diagram bullet list invented 'SS (Pin 14)' and 'IC (Pin 15)' (IC listed twice), called the PGOOD logic a NAND driving a P-channel MOSFET (PDF: OR gate, N-channel open drain) and omitted G_M, V_C compensation, I_SS/C_SS, C_FF and the V_IN pins; the bold markers were broken. Rewritten from the drawing | `ltc3309a-p10-block-diagram-description` | medium |
| 8 | Scope descriptions G28-G36 contained Chinese words (纹波, 电压) and no channel scales; G33 described as 'bursts of pulses' (single pulses with ringing). Rewritten with the printed scales | `ltc3309a-p8-g28` ... `-g36` | low |
| 1, 13, 17-23, 26 | Schematic descriptions contradicted the drawings: input 10µF called output capacitors (TA02-TA05, p26 TA08), 1µF 0201 'in series' (TA06/TA07), 10nF called a SYNC coupling or FB capacitor (TA04, TA08/TA09), invented 1.3M/200k resistors in TA05, TA09 divider given as 200k/200k (PDF: 100k/200k), missing 33µF/47µF x2 output capacitors, 22.6k RT, 1M pull-ups; Fig 1 divider placement, Fig 2 'pin 3' and 'ground labeled 3309A F02', Fig 3a CBYP called a resistor, Fig 4 thermal paths and an invented theta_CV | `ltc3309a-p1-ta01a`, `ltc3309a-p13-fig1`, `ltc3309a-p17-fig2`, `ltc3309a-p18-f03a`, `ltc3309a-p19-fig4`, `ltc3309a-p2[0-3]-ta0*`, `ltc3309a-p21-ta0*`, `ltc3309a-p26-ta08` | low |
| 1, 5, 6, 7 | Curve descriptions: TA01b power-loss levels (0.001W/0.5W; PDF about 0.0003W/0.2W, now described by shape), G01 peak near 50°C, G02/G04/G06 curves start at 2.25V, G10 NMOS end points, G20-G27 line styles (dashed vs dotted, no dash-dot line) | `ltc3309a-p1-ta01b`, `ltc3309a-p5-g0*-desc*`, `ltc3309a-p6-g10`, `ltc3309a-p7-g2*-line-styles` | low |
| 24 | Package drawing: X is a datum; 12b/eee/fff belong to DETAIL A, DETAIL C shows A1 and 12× ddd; land pattern 2.50 ±0.05 is the overall size, not the pitch; 0.70 ±0.05 is the pad length | `ltc3309a-p24-*` | low |
| 1, 5, 8, 13, 17-23, 26 | Drawing numbers missing: TA01a, G01-G09, G28-G36, F01-F04 (F03a/F03b), TA02-TA09 and TA08 on p26 (printed as TA08 on both p23 and p26, kept as printed); Figure 2-4 captions bolded like Figure 1 | `*-drawing-number`, `ltc3309a-p18-fig3-caption-bold` | low |
| 4, 16, 18, 19 | Paragraphs split at the column break were rejoined (Note 2, 'The second function', 'unbroken ground plane', 'relatively high') | `*-column-split` | low |
| 3, 11, 12, 14, 16, 17 | As printed: `VEN =0.5V` (EN Pin Leakage), curly apostrophes (regulator’s, LTC3309A’s ×5), 'RT pin' as a pin name (not R_T), Equation (3) denominator `f_sw` lowercase | `ltc3309a-p3-en-leakage-*`, `*-curly-apostrophe`, `ltc3309a-p14-*` | low |

No error found on p2 (the earlier pinout/order fixes still hold), p9, p15 or p25.
After the fixes: `validate.py --all` reports ltc3309a OK (word/number coverage 99.9/100.0%, unchanged; geometry 37 / 0 / 1 / 91). `check_llm_fidelity.py`: ltc3309a has 0 spec-table failures and the numeric subset is True. `relocate_images.py --check ltc3309a`: OK. `check_struct_tables.py`: unchanged. `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).
`ltc3309a.llm.md` was regenerated with `tools/llm_compact.py ltc3309a`. Every summary claim in `reports/llm/summaries/ltc3309a.md` was re-checked against the corrected md (p1-p4, p9, p11, p12); none needed a change.

Not changed / open:
- Repo-wide conventions were kept: hyphen for the en dash (–40°C, –1.5), Greek μ next to µ, `˚` (U+02DA) in the p2 temperature ranges normalized to `°`, and running headers/footers omitted, including the p25 'Information furnished by Analog Devices…' disclaimer and the p26 copyright line.
- p24 notes 1 and 4-6 are cut off at the right edge in the PDF itself ('OPENING N', 'HEAT F', 'MUST LOCATED', 'OPTIONAL CORN'); the md keeps them truncated as printed.
- p11 'start-up' and p13 'soft-start' are hyphenated at line ends in the PDF; the md hyphenation was kept.
- Structure-only oddities: `#### Overtemperature Protection` at H4 while sibling subsections are H3 (p12), bold `###` headings on p13, the p8 scope channel labels only inside the descriptions.
- Figure descriptions are still AI text. They now agree with the drawings on connections, labels and dimension meanings, but approximate curve levels (for example TA01b "approximately 80% at 0.001A", G06 "1.96 MHz at 2.25V") are estimates. Read values from the image/PDF.

### ltc3313 full page-by-page review (2026-10-26)

Scope: all 29 PDF pages of `ltc3313.pdf`. For each page: rendered image (`tools/review/render_pages.py`, plus 170-300 dpi crops of the schematics, the block diagram, the scope plots and the rotated p27 package drawing), `pdftotext -layout`, PyMuPDF spans (sub/superscripts, glyphs), and a word-level diff of the PDF text against the `{N-1}` section of `output/ltc3313/ltc3313.md`. The EC tables (p3, p4) match the PDF cell by cell, including the ● column and MIN/TYP/MAX positions. Abs Max and the order tables (p2), Tables 1-6 (p13-p16), the p27 dimension table, Revision History (p28) and Related Parts (p29) were checked row by row.
94 new fixes, all `ltc3313-p*` ids in `fixes.json` (9 medium, 85 low). Description fixes have two entries each (`-alt` for the image alt text, `-desc` for the repeated paragraph). `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 1 | Part number title 'LTC3313' was missing; the md started at the subtitle | `ltc3313-p1-title-missing` | medium |
| 10 | Block diagram bullet list had broken bold markers, invented a 'FAULT pin', called SSTT 'Supply Temperature', SENSE+/SENSE- 'pins', connected SLOPE COMP to FB and MODE/SYNC to a resistor, and omitted ITH, R_C/C_C, the 10µA source, the V_TEMP buffer and the PGOOD comparators. Rewritten from the drawing | `ltc3313-p10-block-diagram-description` | medium |
| 23, 24 | TA04/TA05 descriptions invented 'full-bridge' and 'single-phase rectifiers' (TA04), a 2x2 grid, grounded slave ITH/FB/SSTT pins and slave MODE/SYNC driven by the master SW (TA05). Rewritten from the drawings | `ltc3313-p23-ta04-*`, `ltc3313-p24-ta05-*` | medium |
| 26 | TA08 had only an 'Image:' placeholder (no image file was ever extracted), the running header as H1 and the page footer. Replaced by a description written from the drawing, marked as such, plus the drawing number | `ltc3313-p26-*` | medium |
| 27 | Dimension table: D, E, D1, E1, e, H1, H2 are NOM values and aaa-fff MAX values (md had all under MIN). The package drawings were missing and no image exists; their printed labels are now listed by view | `ltc3313-p27-dimension-table-columns`, `ltc3313-p27-drawing-labels` | medium |
| 8 | Scope descriptions G25-G30: I_L is the inductor current, not the load current; invented '200mA peak' (200mA is I_LOAD); SW in pulse-skipping is not a square wave; the load-release overshoot was missing. `22µF ×6` as printed | `ltc3313-p8-g2*`, `ltc3313-p8-g3*` | low |
| 1, 13, 16, 19-22, 25, 29 | Schematic/figure descriptions contradicted the drawings: TA01a (FB divider, 47µF ×3, missing parts), Fig 1 (C_FF across R_A, not to ground), Fig 2 (RT on the R3/R4 node), Fig 3 (split axes, one solid line), Fig 4 (invented C_CS/CS pin, R_T 'temperature sensor'), TA02 (empty alt, now described), TA03 (PGOOD 100k 'to ground', 5.49k/1500pF on every phase), TA06/TA07 (value lists without connections), TA09 (178k is RT, not feedback) | `ltc3313-p1-ta01a`, `ltc3313-p13-fig1`, `ltc3313-p16-fig2`, `ltc3313-p19-fig3`, `ltc3313-p20-fig4`, `ltc3313-p21-ta02-*`, `ltc3313-p22-ta03-*`, `ltc3313-p25-ta0*`, `ltc3313-p29-ta09` | low |
| 1, 5-7 | Curve descriptions: TA01b efficiency 'starts at 100% at 0A' and power loss 3.6W (about 2.8W); G01 15A line dotted; G02 2.5V curve turns down; G03-G08 'vertical line indicating f_SW' (it is a text label); G09, G12, G13, G18, G19 shapes and start points | `ltc3313-p1-ta01b-*`, `ltc3313-p5-*`, `ltc3313-p6-g*`, `ltc3313-p7-g18/g19-desc` | low |
| 1, 7, 13, 16, 19-26, 29 | Drawing numbers missing as text: TA01a (×2, printed twice), G18-G24 (only inside the AI text), F01-F04, TA02, TA05, TA08, TA09; inductor notes on TA02 and TA09; Figure 1, 3, 4 captions bolded like Figure 2 | `*-drawing-number*`, `*-caption`, `ltc3313-p21-ta02-desc-labels`, `ltc3313-p29-ta09-labels` | low |
| 11, 12, 13, 18 | Paragraphs split at the column break were rejoined ('good EMI / performance', 'thermal design / consideration', 'The highest / switching frequency', 'FB pin / voltage') | `*-column-split` | low |
| 1, 9, 11, 15-19, 25 | As printed: LTC®3313 not bold, curly apostrophes (LTC3313’s ×4, comparator’s), `10µA`/`1µs`/`125µs` without spaces, Eq (10) t_SS/C_SS, I_VALLEY(MAX) subscript, Table 6 V_IN, `22µF ×3`/`×2` | `ltc3313-p1-ltc-not-bold`, `*-curly-apostrophe`, `ltc3313-p9-sstt-10ua`, `ltc3313-p17-*`, `ltc3313-p18-*`, `ltc3313-p19-ivalley-max-subscript`, `ltc3313-p16-table6-vin-space*`, `ltc3313-p25-*-as-printed` | low |

No error found on p2 (the earlier pinout fixes still hold), p3, p4, p14 (the earlier Wurth fix holds) or p28.
After the fixes: `validate.py --all` reports ltc3313 OK (word/number coverage 99.7/100.0%; geometry 44 / 0 / 0, 0 table issues). `check_llm_fidelity.py`: ltc3313 has 0 spec-table failures and the numeric subset is True. `relocate_images.py --check ltc3313`: OK (45 images). `check_struct_tables.py`: unchanged. `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).
`ltc3313.llm.md` was regenerated with `tools/llm_compact.py ltc3313`. Every summary claim in `reports/llm/summaries/ltc3313.md` was re-checked against the corrected md (p1-p4, p11, p16, p18); none needed a change.

Not changed / open:
- p26 (TA08) and p27 (package drawings) have no image in `img/`: Datalab did not extract them. The md now carries a description / label list marked as written from the PDF drawing; extracting those images would need a new conversion or a rendered crop.
- p11 says 'See Table 6' and p14 'See Table 4 for pin configuration' (Table 4 is the multiphase configuration; Table 6 has the single-phase pin settings). Kept as printed.
- Repo-wide conventions were kept: hyphen for the en dash (–40°C, –0.3V), Greek μ next to µ, and running headers/footers omitted, including the p28 'Information furnished by Analog Devices…' disclaimer and the p29 copyright/date footer. The p1 FEATURES list prints its first five items in bold; the md does not bold them.
- p15 'X5R or X7R type capacitors' starts the right column; it is ambiguous whether it continues the previous paragraph, so the paragraph break was kept. Same for p19 'In normal operation…'.
- Structure-only oddities: typical-application titles on p21-p24 and p29 are plain text while p25/p26 are bold; label dumps under the p8 and p25 figures; `## LTC3313` running header kept on p2.
- Figure descriptions are still AI text (some rewritten by hand from the drawings). They now agree with the drawings on connections, labels and dimension meanings, but approximate curve levels (for example G10 '~14 mΩ to ~7.5 mΩ', G12 'about 23 μA') are estimates. Read values from the image/PDF.
