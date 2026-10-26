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
- Repo-wide conventions were kept: hyphen for the en dash (–40°C, –0.3V), Greek μ next to µ, and running headers/footers omitted, including the p28 'Information furnished by Analog Devices…' disclaimer and the p29 copyright/date footer. The p1 FEATURES list prints its first five items in bold; the md does not bold them.
- p15 'X5R or X7R type capacitors' starts the right column; it is ambiguous whether it continues the previous paragraph, so the paragraph break was kept. Same for p19 'In normal operation…'.
- Structure-only oddities: typical-application titles on p21-p24 and p29 are plain text while p25/p26 are bold; label dumps under the p8 and p25 figures; `## LTC3313` running header kept on p2.
- Figure descriptions are still AI text (some rewritten by hand from the drawings). They now agree with the drawings on connections, labels and dimension meanings, but approximate curve levels (for example G10 '~14 mΩ to ~7.5 mΩ', G12 'about 23 μA') are estimates. Read values from the image/PDF.

### ltc3315a full page-by-page review (2026-10-26)

Scope: all 26 PDF pages of `ltc3315a.pdf`. Each page was checked as a rendered image (`tools/review/render_pages.py`), as `pdftotext -layout` output and as PyMuPDF words/spans (sub/superscripts, positions in the rotated p23 table and the rotated p24 labels), all compared with the `{N-1}` section of `output/ltc3315a/ltc3315a.md`. The EC tables (p3, p4) match the PDF cell by cell, including the ● column and the MIN/TYP/MAX positions. Also checked row by row: Abs Max and the pinouts (p2), the order tables (p3), Table 1 and Table 2 (p16), the LQFN dimension table (p23), Revision History (p25) and Related Parts (p26).
82 new fixes, all `ltc3315a-p*` ids in `fixes.json` (5 medium, 77 low). Description fixes have two entries each: `-alt` for the image alt text and `-desc` for the repeated paragraph. `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 1 | The part number title 'LTC3315A' was missing; the md started at the subtitle | `ltc3315a-p1-title-missing` | medium |
| 11 | Pin label `PGGOOD 5, A1` (PDF: PGOOD). The block diagram paragraph had FB going through a resistor to G_M, V_IN pins as 'outputs', 'a 0.5V reference and a 0.5V reference', and MODE DETECTION fed by the references. It omitted the OR gate enabling OSCILLATOR/OT detect, the 180° inverter, the 0.55V/0.49V PGOOD comparators and the open-drain NMOS. Rewritten from the drawing | `ltc3315a-p11-pin-label-pgood`, `ltc3315a-p11-block-diagram-*` | medium |
| 23 | LQFN dimension table: D, E, D1, E1, e, H1, H2 are NOM values (word positions in the rotated table); the md had them under MIN | `ltc3315a-p23-dimension-table-nom-column` | medium |
| 24 | WLCSP drawing number `PKG-00000000` placeholder; the PDF prints `PKG-006559` | `ltc3315a-p24-pkg-number` | medium |
| 1, 20-22, 26 | Schematic descriptions contradicted the drawings. TA01a: EN1/EN2 'connected to VIN', f_SW 'connected to MODE/SYNC', missing 33µF/22µF. TA02: MODE/SYNC 'to ground', feedback R/C 'in parallel to ground', broken bold markers. TA03-TA06: values without connections, missing 1µF 0201 (TA04) and feed-forward caps (TA05/TA06). TA07: invented cross-connection of the outputs, while the PDF shows V_OUT1 → 169k/100k/0.1µF → EN2 sequencing. All were rewritten from the drawings | `ltc3315a-p1-ta01a-*`, `ltc3315a-p20-ta02-description`, `ltc3315a-p2[12]-ta0*-description`, `ltc3315a-p26-ta07-*` | low |
| 8, 9 | G25-G31 descriptions contained the Chinese word '参数', `fsw`, `uH`. Scope descriptions G32-G37: the Burst Mode pulses were placed during the load step or start-up ramp (they occur at light load / after the ramp), the overshoot at load release and the printed 5A/µs were missing, and I_L was only a 'small initial spike' | `ltc3315a-p8-g2*`, `ltc3315a-p8-g3*`, `ltc3315a-p9-g3*` | low |
| 14, 18, 19, 24 | Figure 1: C_FF is across R2, not R1, and FB is not grounded. Figure 3 layout: an invented pin 18, 'C1N1/C1N2', 'input inductors', and the Kelvin note misread as 'R1, R3, and R4'. Figure 4: θ_CB/θ_BA meanings. WLCSP views: 0.40 REF is the C-D row pitch; the end-view ball diameter/pitch values were misassigned and the coplanarity was placed at the top of the package | `ltc3315a-p14-fig1-*`, `ltc3315a-p18-fig3-*`, `ltc3315a-p19-fig4-desc`, `ltc3315a-p24-wlcsp-*` | low |
| 1, 5-7 | Curve descriptions: TA01b turns down above 1A; G05 is not monotonic; G09 'especially BOTH BUCKS'; G15 peak at 0.5-1A, not 100-200mA; G17 line styles | `ltc3315a-p1-ta01b-*`, `ltc3315a-p5-g05-*`, `ltc3315a-p6-g09-*`, `ltc3315a-p6-g15-*`, `ltc3315a-p7-g17-*` | low |
| 1, 8, 9, 14, 17-24, 26 | Drawing numbers added as text: 3315A TA01a/TA01b/TA02-TA07, 3315ab G25-G37, F01-F04, LQFN 12 0618 REV B (some were only inside the AI text). Figure 1-4 captions bolded as printed | `*-drawing-number*`, `*-caption-bold`, `*-desc` | low |
| 4, 12, 16, 18, 19 | Paragraphs split at the column break were rejoined (Note 2, start-up delay, C_OUT bandwidth, PCB item 3, θ_JA vias) | `*-column-split`, `ltc3315a-p18-pcb-list-item3` | low |
| 2, 3, 5, 10, 12-14, 16-18 | As printed: curly apostrophes (buck’s ×2, regulator’s ×3, LTC3315A’s ×2), the G06 title V_IN subscript, no trailing comma after ΨJB = 15°C/W, flat order-note bullets, PCB Considerations as an H3 subsection with a numbered 1-4 list | `*-curly-apostrophe*`, `ltc3315a-p5-g06-title-vin-subscript`, `ltc3315a-p2-wlcsp-thermal-trailing-comma`, `ltc3315a-p3-order-*`, `ltc3315a-p17-pcb-considerations-heading-level`, `ltc3315a-p18-pcb-list-numbering` | low |

No error found on p15 or p25. The earlier p3/p4 EC fixes, p2 ball map and p16 Würth fixes still hold.
After the fixes: `validate.py --all` reports ltc3315a OK, with word/number coverage going from 99.8/99.8% to 99.8/100.0% (p23 now 100%) and 0 table issues. `check_llm_fidelity.py`: ltc3315a has 0 spec-table failures and the numeric subset is True. `relocate_images.py --check ltc3315a`: OK (54 images). `check_struct_tables.py`: unchanged. `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).
`ltc3315a.llm.md` was regenerated with `tools/llm_compact.py ltc3315a`. Every summary claim in `reports/llm/summaries/ltc3315a.md` was re-checked against the corrected md (p1-p4, p12, p13); none needed a change.

Not changed / open:
- Repo-wide conventions were kept. The md uses a hyphen or minus sign (−) where the PDF prints an en dash (–40°C, –0.3V), and Greek μ appears next to µ. Running headers/footers are omitted, including the p25 'Information furnished by Analog Devices…' disclaimer and the p26 copyright/date footer. The repeated `## OPERATION` / `## APPLICATIONS INFORMATION` page headers are kept.
- Structure-only oddities: the typical-application titles on p20/p21 are plain text while those on p22/p26 are `###` headings; the p8 graph titles are LaTeX and not bold, unlike p7; the p4 EC table has its own ● column for Power Good and Oscillator but not for the first rows; `- NOTES:` is a bullet on p23. Paragraphs split by a figure at the column break (p14 'helps cancel / the pole', p17 'this threshold can / be adjusted') were left split, as were the page-break splits on p15/p16 and p17/p18.
- Figure descriptions are still AI text, and several were rewritten by hand from the drawings. They now agree with the drawings on connections, labels and dimension meanings, but approximate curve levels (for example TA01b '~80% at 1mA', G06 '1.96 MHz at 2.25V') are estimates. Read values from the image/PDF.

### max31730 full page-by-page review (2026-10-26)

Scope: all 48 PDF pages of `max31730.pdf`. Each page was checked as a rendered image (`tools/review/render_pages.py`, plus 250-300 dpi crops of the typical application circuits, the timing diagrams and Figure 4), as `pdftotext -layout` output and PyMuPDF text (curly apostrophes, sub/superscripts), and with a per-page word/number multiset diff between the PDF text and the `{N-1}` section of `output/max31730/max31730.md`. The EC, Recommended and I2C AC tables (p2-p4) match the PDF cell by cell, including MIN/TYP/MAX positions. Also checked row by row: Abs Max and thermal (p2), the pin description (p6, p7), Tables 1-17, the register map (p22-p24), every register bit table (p24-p44: access row, field row, weight row, Bit 7/Bit 0 positions, factory default), ordering/package information (p47) and revision history (p48).
89 new fixes, all `max31730-p*` ids in `fixes.json` (23 medium, 66 low). Description fixes have two entries each: `-alt` for the image alt text and `-desc` for the repeated paragraph. `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 6 | Pinout description said the µMAX is a 12-pin package with pins 1-12 (the drawing has 10 pins); TDFN body label 'MA31730' noted as printed | `max31730-p6-pinout-10pin-*` | medium |
| 8 | Block diagram description listed 'DXP1, DXP2, DXP3' as both inputs and outputs, never named DXN1-DXN3 and called the sensors diodes. Rewritten from the drawing (diode-connected PNPs, input selector into MUX, current source, REF, ADC, register bank, ALARM to THERM, SMBus/I2C interface) | `max31730-p8-block-diagram-*` | medium |
| 19 | Figure 4 description had the PNP emitter on DXN and base on DXP; the drawing (and the text) has emitter on DXP, base on DXN | `max31730-p19-fig4-*` | medium |
| 25-41 | Register bit tables: 'Bit 0' on a separate row under the first bit column (01h-07h, 10h), under a middle column (13h, 1Bh, 1Ch, 20h, 33h, 36h, 40h, and 'Bit 7' in the label column for 13h/14h), or in a spurious 10th column (32h). The PDF prints Bit 7 under the first and Bit 0 under the last bit column. 14h: 'See Table 8' spans the bit columns, not the label column | `max31730-p2[5-8]-reg*`, `max31730-p3[3-8]-reg*-bit0-column`, `max31730-p41-reg*` | medium |
| 1, 5, 10, 11, 46 | Figure descriptions: typical application circuits rewritten from the drawing (shared DXN on µMAX, filter capacitors, ADD resistor, THERM pullup); toc03 'slight increase' (curves bend up at the hot end); toc04 estimated error range removed; Figure 1 had empty alt text (shaded = slave-transmission cells listed); Figure 2/3 descriptions contradicted their printed legends (Figure 3 was a copy of Figure 2); Figure 5 traces called layers and trace width missing | `max31730-p1-typ-app-*`, `max31730-p5-toc0*`, `max31730-p10-fig1-alt`, `max31730-p11-fig*`, `max31730-p46-fig5-*` | low |
| 11 | Figure 2/3 legends: 'R/W' printed with an overbar on W | `max31730-p11-fig*-rw-overbar` | low |
| 45 | Unused Diode Channels: DXP_/DXN_/THERM wrapped in backtick code spans, so the overline `<span>` showed as literal HTML | `max31730-p45-unused-channels-no-code-spans` | low |
| 1 | THERM in the General Description was bold; the PDF only overlines it | `max31730-p1-therm-not-bold` | low |
| 11-14 | Paragraphs split at the column break rejoined (ARA 'alert still / exists', 'temperature data / format', 'The Reference / Temperature', 'continuous-conversion mode. / In standby mode') | `*-column-split` | low |
| 3-47 | Heading levels as printed: teal section titles as H2 (I2C AC EC, Pin Description, Register Map ×3, Chip Information), bold black subsections as H3 (Temperature Channel Enable, Highest Temperature ×2, Thermal-Limit, Configuration, THERM Mask, Beta Compensation, PCB Layout); bold markers removed from Pin Description (continued), Status Register Functions and 12 register titles (24h-31h, 44h-51h) | `*-heading-*` | low |
| 4-48 | As printed: curly apostrophes (SCL’s, byte’s, registers’, channel’s ×2, cable’s, Integrated’s), 'tolerence' (Table 17 note), PCB Layout as a 1)-4) list without bullets, Table 1/2/9 (continued)/10/12/13 captions bold like Tables 3-8, Figure 5 caption not bold like Figures 1-4 | `*-curly-apostrophe*`, `max31730-p46-*`, `*-caption-*` | low |

No error found on p2, p3 (apart from the heading level), p7 (apart from the heading), p9 (apart from the apostrophe), p16, p21, p27, p29-p31, p34, p35 (apart from headings), p39, p40, p42 or p43-p44 bit tables. The earlier THERM overbar, DXN_ and p35/p43 Bit 0 fixes still hold.
After the fixes: `validate.py --all` reports max31730 OK (word/number coverage 99.9/100.0%, 0 table issues; p46 went from 99.5% to 100% once 'tolerence' and the '- 1)' list markers were fixed). `check_llm_fidelity.py`: max31730 has 0 spec-table failures and the numeric subset is True. `relocate_images.py --check max31730`: OK (12 images). `check_struct_tables.py`: unchanged (max31730 23 loose rows, 0 misplaced fields). `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests). `reports/validation/SUMMARY.md` now lists all datasheets again (the committed copy had a single row).
`max31730.llm.md` was regenerated with `tools/llm_compact.py max31730`. Every summary claim in `reports/llm/summaries/max31730.md` was re-checked against the corrected md (p1-p3, p7, p8, p14, p45); none needed a change.

Not changed / open:
- Manufacturer inconsistencies kept as printed: register 18h's bit table is labeled '1Ch' (p31); 14h says 'See Table 8' (the ideality table is Table 9); 14h is titled 'Customer Ideality Factor'; 51h shows factory default 01h but all-zero bits; Table 12 title 'and1Ch'; Table 5/13h EXTRANGE text (p14) says logic 1 selects +127.9375°C while the 13h table (p28) says 0 = +127.9375°C (default), 1 = +191.9375°C; the TDFN pinout body label 'MA31730'.
- Repo-wide conventions kept: LaTeX for some formulas, units and symbols (`$\mu$ MAX`, `$t_{LOW}$`, p4 notes, toc axis labels); the PDF's 'º' (U+00BA) in the register-table '°C' row labels rendered as '°'; hyphen-minus for negative values as printed; Greek μ and micro µ both present. Register titles remain H4 under the Register Map section, although the PDF prints them in the same bold style as the H3 subsections.
- Paragraphs interrupted by a figure were left split (p19 'Note that if beta compensation is enabled, the' / Figure 4 / 'series resistance...'), as in earlier reviews.
- Figure descriptions are still AI text (several rewritten by hand from the drawings). Curve descriptions give shapes only; read values from the image/PDF.

### ad5593r full page-by-page review (2026-10-26)

Scope: all 47 PDF pages of `ad5593r.pdf`. Each page was checked as a rendered image (110-200 dpi pages plus 220-900 dpi crops of the block diagram, the pinouts, Figure 35, the I2C sequence drawings, the bit maps and the package drawings), as `pdftotext -layout` output and PyMuPDF words/spans (positions, fonts, sub/superscripts), and with a per-page word/number multiset diff between the PDF text and the `{N-1}` section of `output/ad5593r/ad5593r.md`. Table 2 (p3-p5) and Table 3 (p6) match the PDF cell by cell, including the Min/Typ/Max/Unit positions. Also checked row by row: Abs Max and Table 5/6 (p7), the pin table (p8), Tables 8-10 (p28-p29), every bit-description table (Tables 11-34, p29-p45), the ordering guide and evaluation boards (p47).
172 new fixes, all `ad5593r-p*` ids in `fixes.json` (23 medium, 149 low). Description fixes have two entries each: `-alt` for the image alt text and `-desc` for the repeated paragraph. `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 1 | Part number title 'AD5593R' was missing | `ad5593r-p1-title-missing` | medium |
| 8 | WLCSP ball map described as 'Pin 1' to 'Pin 16' instead of balls A1-D4; drawing numbers 003/004/201 called pins | `ad5593r-p8-fig5-wlcsp-ball-map`, `ad5593r-p8-fig3-*`, `ad5593r-p8-fig4-*` | medium |
| 19 | Figure 35 ADC input structure: 5.8pF placed after S1 on the U1 output, 300Ω before the 23.1pF capacitor, S1/S2/S3 roles wrong. Rewritten from the drawing | `ad5593r-p19-fig35-adc-input-structure` | medium |
| 21, 22 | Figures 37-39: invented pointer byte '9100000000000000', master acknowledging each bit, missing stop/start between the write and read transactions; Figure 38 was a copy of 37; Figure 39 frames 3/4 swapped and note 1 on the wrong frame. Rewritten from the drawings | `ad5593r-p21-fig37-*`, `ad5593r-p21-fig38-*`, `ad5593r-p22-fig39-*` | medium |
| 24 | Figure 41 table lost the printed byte values 0b1010XXX / 0bXXXXXXX ('DACADDRESS' as printed), an A field and the overbars | `ad5593r-p24-fig41-*` | medium |
| 33 | GEN_CTRL_REG bit map: description had [6:3] RESERVED, [2] DAC_RANGE, [1] ADC_RANGE, [0] ALL_DAC; the PDF has [6] ALL_DAC, [5] ADC_RANGE, [4] DAC_RANGE, [3:0] RESERVED | `ad5593r-p33-gen-ctrl-bitmap-*` | medium |
| 46 | Package descriptions read max/nom/min stacks as separate top/bottom body sizes ('5.10 x 6.40 mm body with 4.90 x 6.40 mm pin pitch', '3.10 x 3.10 top / 3.00 x 3.00 bottom', '2.000 / 1.960'); the WLCSP label list carried the LFCSP '0.50, 0.40, 0.30'; TSSOP end-view dimensions, pin labels and the date codes 09-03-2013-A / 10-17-2012-B were missing | `ad5593r-p46-fig4*-dimensions`, `ad5593r-p46-fig4*-labels`, `ad5593r-p46-fig4*-drawing-id*` | medium |
| 47 | Marking code DM6 was on the WLCSP row; the PDF prints it on the AD5593RBCPZ-RL7 (LFCSP) row | `ad5593r-p47-marking-code-row` | medium |
| 1, 9-13, 18, 20, 25, 27, 37, 42, 44, 45 | Figure descriptions: block diagram (invented 'SW', no sequencer/T/H), Figure 6/8 INL 'positive slope', Figure 12 -6 dB 'at 10 MHz', Figures 13-17 shapes and glitch levels, Figures 20/21 two overlaid curves, Figures 26/27 curves are DAC codes, Figures 25/29 'log-log' (NSD axis is linear), Figures 24/28 p-p estimates, Figure 34 '035' axis label, Figure 36 frame bits, Figure 42 Step 3 and 'SCL line', Figure 43 RESET overbar, bit-map labels/names (GPIO_CONFIG [7:4], open-drain note, DAC_WRITE/DAC_READBACK, 12 zeros for 11 bits) | `ad5593r-p1-fig1-*`, `ad5593r-p9-*`, `ad5593r-p1[0-2]-fig*`, `ad5593r-p18-fig34-*`, `ad5593r-p20-fig36-*`, `ad5593r-p25-fig42-description-*`, `ad5593r-p27-fig43-*`, `ad5593r-p37-*`, `ad5593r-p42-*`, `ad5593r-p44-*`, `ad5593r-p45-*` | low |
| 2, 23, 25 | Spurious table separator rows (revision history, Figure 40); Figure 42 header row repeated the STEP1 data, last A/A̅ lost its first A; Figure 40 W overbar | `ad5593r-p2-revision-history-stray-separator`, `ad5593r-p23-fig40-*`, `ad5593r-p25-fig42-header-row`, `ad5593r-p25-fig42-final-ack-nack` | low |
| 19-25, 28 | Paragraphs split at the column break rejoined (reset, 'transi-/tions', 'can then/follow', 'input and output,/the primary', 'and setting/the LDAC', 'repeats the/sequence'); p28 'Table 10 shows…' paragraph moved back to the left column order | `*-column-split`, `ad5593r-p28-reading-order` | low |
| 2-47 | Heading levels as printed: blue section titles (repeated on every page) H2, black bold caps subsections H3, black bold title-case subsections and register titles H4; all TERMINOLOGY entries H3; '85 KΩ PULL-DOWN PINS' as printed | `*-heading-level`, `ad5593r-p14-term-*`, `ad5593r-p15-term-*`, `ad5593r-p26-85k-pulldown-heading` | low |
| 14, 19, 26, 46 | As printed: ellipsis U+2026 in the code transitions, I/Ox and I/O0 without subscripts, '250 μs', '3 mm × 3 mm' in the Figure 45 caption | `ad5593r-p14-ellipsis-*`, `ad5593r-p*-io-not-subscript-*`, `ad5593r-p26-250us`, `ad5593r-p46-fig45-caption-times` | low |

No error found on p3, p4, p5 (Table 2), p17, p29-p32, p34-p36, p38-p41, p43 (apart from the repeated heading levels). The earlier ad5593r fixes (f_IN header row, Table 18 rows, RESET overbars, 'both and input', ESI, Figure 42 binary values, removed curve tables) still hold.
After the fixes: `validate.py --all` reports ad5593r OK (word/number coverage 100.0/99.8%, was 99.9/99.8%; geometry 132 / 0 / 5, 0 table issues). The remaining number misses are tokenization artifacts: p15 '4' from the LaTeX ¼/¾ fractions, p19 '-0.5' from '−(0.5 / V_REF)'. `check_llm_fidelity.py`: ad5593r has 0 spec-table failures and the numeric subset is True. `relocate_images.py --check ad5593r`: OK (71 images). `check_struct_tables.py`: unchanged (32 tables, 1 loose row, 0 misplaced fields). `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).
`ad5593r.llm.md` was regenerated with `tools/llm_compact.py ad5593r` (the section index now lists the H2 sections at their printed level). Every summary claim in `reports/llm/summaries/ad5593r.md` was re-checked against the corrected md (p1, p3-p6, p8, p17, p18, p20, p26); none needed a change.

Not changed / open:
- Manufacturer errata kept as printed: Table 2 SNR second row 'VDD = 5.5 V' (the SINAD/THD/SFDR rows use 3.3 V); p18 'Calculate the input current for buffered mode' twice (the second is unbuffered), 'Switch S2 is closed' for both modes, 'the voltage that on'; p19 'both and input'; Figure 41 '0b1010XXX' / '0bXXXXXXX' with 7 bit positions and 'DACADDRESS'; Figure 38 'ACK. BY MASTER' before the stop; Table 19 ADC_RANGE text 'ADC gain is 0 V to VREF'.
- Repo-wide conventions kept: hyphen-minus for negative values, LaTeX for formulas and some units (`$\mu$`, `$\Omega$`, `\frac{1}{4}`), `<b>` on the Table 2 section rows (not bold in the PDF), table captions sometimes bold or italic, the Table 7 'Pin No.' header as two rows, the p1 disclaimer and p47 copyright/address footer omitted. The bit-map images on p31 and p45 also carry a transcription of their bit rows below the image.
- Paragraphs split at page breaks (p22/p23 'write to the appropriate register and / set the corresponding bit') were left split, as in earlier reviews. 'Reset: 0x…, Name: …' lines are bold in the PDF and plain in the md.
- Figure descriptions are still AI text (many rewritten from the drawings). Curve descriptions give shapes only; the remaining approximate levels (for example Figure 18/19 '2.43 V'/'2.56 V') are estimates. Read values from the image/PDF.

### ad5711r-ad5710r full page-by-page review (2026-10-26)

Scope: all 60 PDF pages of `ad5711r-ad5710r.pdf`. The review ran across two sessions: p1-p31 in the first, p32-p60 in the second, which also re-checked the uncommitted p32-p36 edits the first session left behind. Each page was checked four ways: as a rendered image (`tools/review/render_pages.py`, plus 230-400 dpi crops of the block diagram, timing diagrams, the ball map, Figures 55-76, every register bit map and the outline drawing); as `pdftotext -layout` output; as PyMuPDF words/spans (positions, fonts, sizes, colors, sub/superscripts); and with a per-page word/number multiset diff between the PDF text and the `{N-1}` section of `output/ad5711r-ad5710r/ad5711r-ad5710r.md`. Also checked cell by cell or row by row:
- spec tables: the DC/AC specification tables (p4-p8), Table 4/5 timing (p9-p10), Abs Max and thermal (p11), the ball table (p12);
- other tables: Tables 10-16 (p25-p39), Table 17 register summary (p40-p41; each field against its PDF bit column, plus Reset/Access);
- every register bit map and bit-description table (Tables 18-50, p42-p59; bit values against the Reset value, bracket ranges), and the ordering guide (p60).
226 new fixes, all `ad5711r-ad5710r-p*` ids in `fixes.json` (34 medium, 192 low). Description fixes have two entries each: `-alt` for the image alt text and `-desc` for the repeated paragraph. `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 1 | Part number title 'AD5711R/AD5710R' was missing. Block diagram description had IOUT-only outputs, an invented VDD, and MUX inputs as pins. Rewritten from the drawing | `ad5711r-ad5710r-p1-title-missing`, `ad5711r-ad5710r-p1-fig1-*` | medium |
| 9, 10, 12 | Figure 2 description gave wrong meanings for most timing parameters; Figure 4 had one LDAC pulse and wrong t_L1-t_L4 definitions; Figure 5 ball map used 'Pin 1'-'Pin 5' instead of balls A1-E5. Rewritten from the drawings and Tables 4/5/8 | `ad5711r-ad5710r-p9-fig2-description`, `ad5711r-ad5710r-p10-fig4-description`, `ad5711r-ad5710r-p12-fig5-*` | medium |
| 24, 25, 29 | Figure 55 DAC channel block diagram (REFERENCE_CONTROL_0/CHN_VMODE_EN on the wrong blocks, missing REF/buffer/switch); Figure 56 mode-switching diagram ('not recommended' invented, power-down states missing); Figure 58/59 flowcharts (invented YES branches, missing loops, field names) | `ad5711r-ad5710r-p24-fig55-*`, `ad5711r-ad5710r-p25-fig56-*`, `ad5711r-ad5710r-p29-fig5*-flowchart` | medium |
| 32, 33, 36 | Figures 66-70, 74, 75: the AI text put the write data/instruction on SDO and the read data on SDI; SDO Z and SDI DON'T CARE phases were missing. Rewritten from the drawings | `ad5711r-ad5710r-p32-fig6*`, `ad5711r-ad5710r-p33-fig*`, `ad5711r-ad5710r-p36-fig7*` | medium |
| 35, 38 | Figure 73 rewritten with the address-pin straps (U0 to U3) as drawn. Figure 76 had SDI driving the ADuCM320 and SDO driven by it; the PDF has P0.2/MOSI0 → SDI and SDO → P0.1/MISO0 | `ad5711r-ad5710r-p35-fig73-*`, `ad5711r-ad5710r-p38-fig76-*` | medium |
| 43, 54, 56, 58 | Bit-map descriptions. Figure 79: 'Bits 7-3' / 'Bits 2-0', drawn as 7-2 / 1-0. Figure 101/102: invented [15:8]/[7:0] sub-brackets, and Figure 102 named after its field. Figure 104: reserved field called '3-bit', drawn as 7-bit. Figure 105/108 named after their fields | `ad5711r-ad5710r-p43-fig79-*`, `ad5711r-ad5710r-p54-fig10*`, `ad5711r-ad5710r-p56-fig10*`, `ad5711r-ad5710r-p58-fig108-*` | medium (p43, p54), low |
| 60 | The outline drawing (vector, no image) was only a title placeholder; its printed dimension stacks, view labels and drawing numbers PKG-008029 / 03-02-2023-A were added. The running header ('Data Sheet', 'AD5711R/AD5710R', rule) and footer ('analog.com' run into 'Rev. C \| 60 of 60') were in the md on this page only and were removed | `ad5711r-ad5710r-p60-outline-drawing-description`, `ad5711r-ad5710r-p60-running-header-removed`, `ad5711r-ad5710r-p60-footer-removed` | medium, low |
| 40, 41 | Table 17 rows carried 12 (p40) and 7 (p41) empty cells after Access; on p41 the bit names were split with `<br>` at different points than printed ('MI_SEL_CH<br>_3' for 'MI_SEL_CH_/3'). Empty columns removed, names joined; every field re-checked against the PDF bit columns | `ad5711r-ad5710r-p40-table17-empty-columns`, `ad5711r-ad5710r-p41-table17-*` | low |
| 46 | Figure 87-89 description paragraphs appeared twice | `ad5711r-ad5710r-p46-fig8*-duplicate-description` | low |
| 13-20, 30, 31, 49 | Curve/timing descriptions: legends, victim/attacker channels, colors, linear axes, removed estimated levels (Figures 6-53), Figure 60-65 traces (no SCLK/LDAC traces where none is drawn), Figure 93 brackets | `ad5711r-ad5710r-p1[3-9]-fig*`, `ad5711r-ad5710r-p20-fig*`, `ad5711r-ad5710r-p3[01]-fig6*`, `ad5711r-ad5710r-p49-fig93-*` | low |
| 13, 15, 26, 30, 31, 37 | Overbars and subscripts as printed: LDAC/CS/RESET overbars (Option 2/4 text, Figure 61 caption, Hardware Reset), R_SENSE/T_MEAS/I_OUTx/PVDDx subscripts, TPC condition subscripts, Figure 20-22 captions | `*-overbar*`, `*-subscript*`, `ad5711r-ad5710r-p15-fig2*-caption-*`, `ad5711r-ad5710r-p37-hardware-reset-overbars` | low |
| 9, 22, 28, 32-40 | Paragraphs split at the column break rejoined (Table 4 notes, glitch impulse, hardware LDAC, CRC, device addressing, 'every CRC / code', 'for example, / ceramic', 'error flags in the / INTERFACE_STATUS_A'). p37: the software reset subsection moved after Hardware Reset (PDF column order) | `*-column-split`, `ad5711r-ad5710r-p9-table4-notes-split`, `ad5711r-ad5710r-p37-reset-reading-order-heading-level` | low |
| 2-60 | Heading levels as printed: blue section titles H2 (TOC, Revision History, Specifications, Abs Max, Theory of Operation, DAC Core Functions, Digital Interface, Applications Information, Registers, Outline Dimensions); black bold caps subsections H3; title-case subsections and all register titles H4 (some were H3 or H5) | `*-heading-level` | low |
| 7, 22, 28, 30, 36, 37, 57 | As printed: 'ixternal', 'the ideal . The Ideal', 'can be check', 'DAC_Ch0', 'REGISTER_ PARTIAL_ACCESS_ERR' (space after the underscore, twice on p36), 'Sofware Reset', 'affectINPUT_CH4' | `*-as-printed`, `ad5711r-ad5710r-p36-register-partial-access-err-space` | low |

No error found on p5, p6, p8 (the earlier EC table fixes still hold), p11 (apart from the heading), p27 (apart from the caption/alt), p34 (apart from the reading order of Figure 72 and its bullets), p39 (Table 16 equations), p44, p48, p51-p53, p55 or p59.
After the fixes: `validate.py --all` reports ad5711r-ad5710r REVIEW. Word/number coverage went from 99.8/99.7% to 99.9/100.0%. The low-coverage page count went from 1 to 0 (p60 had 82.4% numbers before the outline drawing description). Geometry is 155 / 0 / 15 / 247. The 2 table issues are the p5 Headroom 70/50 and Footroom 250/120 MIN > TYP rows, printed that way (see the EC review above). The remaining single-word misses are a tokenizer artifact: `normalize()` turns `$\overline{\text{LDAC}}$` into 'overlineldac', so p34/p37 lose 'ldac' because every LDAC on those pages is overlined. p22 and p39 lose 'degc' because the md writes °C in LaTeX. Other checks:
- `check_llm_fidelity.py`: 0 spec-table failures (10 tables, 731 cells); the numeric subset is True.
- `relocate_images.py --check ad5711r-ad5710r`: OK (110 images).
- `check_struct_tables.py`: 42 tables, 169 rows (ok 147, loose 19, unpaired 3), 0 misplaced bit-layout fields. Only the Table 17 rows changed, because their empty columns are gone.
- `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).

`ad5711r-ad5710r.llm.md` was regenerated with `tools/llm_compact.py ad5711r-ad5710r`. Every summary claim in `reports/llm/summaries/ad5711r-ad5710r.md` was re-checked against the corrected md (p1, p4, p12, p24, p25, p28): supplies, ranges, DNL/headroom, 3ppm/°C reference, 50/25MHz SPI, WLCSP size, default high-Z IDAC, 50mA source / 10mA sink, 27:1 multiplexer. None needed a change.

Not changed / open:
- Manufacturer errata kept as printed:
  - p7 'ixternal reference'; p22 'the ideal . The Ideal'; p28 'can be check'; p30 'DAC_Ch0'.
  - p34 'LOOP__COUNT' (double underscore); p36 'REGISTER_ PARTIAL_ACCESS_ERR'; p37 'Sofware Reset'.
  - p38 'a data input signal (MISO), a data output signal (MOSI)' (named from the device side), with the ADuCM320 LDAC drawn without an overbar.
  - p48 'Channel Disabled: : VMODE' (MODE_CH_1/0); p55 'MUTLI_DAC_SEL_0' (Figure 103 caption) and 'CHannel'.
  - p57 'affectINPUT_CH4'. In Table 47 the MI_SEL rows say 'write operation on MULTI_DAC_CH does not affect…', and MI_SEL_CH_0 refers to MULTI_INPUT_SEL_CH0.
  - p57/p58 SW_LDAC_TRIG_B mentions SW_LDAC_EN_1 to SW_LDAC_EN_3, which do not exist in the register map.
  - p59 'VMODE enable register..' and the missing periods on CH5/CH0.
- Repo-wide conventions kept: hyphen-minus for printed minus signs (ordering guide '-40 to 125°C'), LaTeX for formulas and overbars, plain-text cross-references alongside `[Figure N](#)` links, the p60 Legal Terms text kept as page content. The DAC_CHn/INPUT_CHn address lists (p54, p58) are bullets in the md and plain lines in the PDF. Table 12 and Table 14 put their spanning MSB/LSB and Streaming Mode header cells in the first column of the span. The MUX_OUT_SELECT bit map (p51) also carries a transcription of its bit row below the image.
- Figure descriptions are still AI text, and many were rewritten from the drawings. Bit-map descriptions now match the drawings and reset values. Curve descriptions give shapes only; read values from the image/PDF.

### ltc2975 full page-by-page review (2026-10-26)

Scope: all 108 PDF pages of `ltc2975.pdf`. p1-p4 were reviewed in the main session; p5-p108 in seven parallel range reviews (p5-17, p18-30, p31-45, p46-60, p61-75, p76-90, p91-108) that shared one written brief (conventions below) and wrote fix batches only; the main session spot-checked each batch against the PDF (e.g. the p7 N_CS command names, p38 'Mfr_ config _dac_mode' and 'CONTROL0 ,' spacing, p53 I_OUT subscript, p66 'STATUS_MFR._SPECIFIC', p83 table headers, p101 Figure 45 '0xB8'), then applied and committed them a few pages at a time. Each page was checked as a rendered image (110 dpi page, 200 dpi halves, 200-400 dpi crops of tables, schematics, timing diagrams and the pinouts), as `pdftotext -layout` output, as PyMuPDF words/spans (positions, fonts, sizes, sub/superscripts, rotated pin labels) and with a per-page word/number multiset diff against the `{N-1}` section of `output/ltc2975/ltc2975.md`. Checked cell by cell: the EC tables (p5-p10, including every MIN/TYP/MAX/UNIT position), the pin tables (p16-p17), Table 3 (p23), the PMBus Summary Table (p25-p30, 121 rows), every command-description table and every "Data Contents" bit table (p31-p84), the fault-log tables and the read example (p76-p83, bytes 0-254), the BGA pinout table and package dimensions (p105-p106), the revision history (p107) and Related Parts (p108).
463 new fixes, all `ltc2975-p*` ids in `fixes.json` (0 high, 97 medium, 366 low). Description fixes have two entries each (`-alt` / `-desc`). `replay_fixes.py` reproduces the md exactly. No EC value or column error was found: the earlier ltc2975 EC fixes still hold.

Conventions applied (from the PDF typography): running section title (LinearBauhaus 18pt) `##`; bold caps 11.7pt subsections `###`; bold-oblique command names and bold title-case subheads `####`, without `**`/`***` inside headings; "X Data Contents" table captions, figure captions, "Summary Table" and the fault-log table titles are bold paragraphs, text as printed; Typical Performance Characteristics graph titles `###`; running header 'LTC2975' and footer 'Rev. D' removed where they had leaked (p4, p16, p58, p97, p104).

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 1 | Part number title 'LTC2975' missing; 'Operate autonomously'. Typical Application: title was an H1, schematic had an empty alt (written from the drawing, plus '2975 TA01'); the vector 'Power Measurement Error' graph (2975 TA01b) was missing entirely (axes/legend/conditions added, no curve values) | `ltc2975-p1-*` | medium |
| 4 | Pinout description named no pins: rewritten with every QFN pin 1-65 and BGA ball A1-J7 (cross-checked with p16-p17); θJCTop → θJCtop (x2); leaked '## LTC2975' | `ltc2975-p4-*` | medium, low |
| 7, 9 | N_CS conditions and the VIN_ON/VIN_OFF parameter are printed as command names (IOUT_OC_FAULT_LIMIT • IOUT_CAL_GAIN), not I/V symbols; symbols as printed (N_ADC, N_V_DAC, TUE_VS ...), CONTROLn (italic n, not a subscript), 'ASEL0,ASEL1' | `ltc2975-p7-*`, `ltc2975-p6-*`, `ltc2975-p9-*` | medium, low |
| 11-15 | Timing diagram description wrong (START/STOP, data phases); graph labels 'IOOUT_CAL_GAIN', 'V_SENSE1', 'READ_TEMPperature_1/_2', 'iiin_range' (x3), 'Total Unbalance Error'; curve descriptions: estimated values removed, G04-G06 are not histograms, G21/G22/G25-G27 curves are temperatures, G10/G12/G13/G23/G24 shapes | `ltc2975-p11-*` ... `ltc2975-p15-*` | medium |
| 18, 20 | Block diagram description wrong in several places (invented '58 pins'), '2975 BD'; Figure 1 AUXFAULTB circuit (current-source pull-up, latch SET/RESET, fault_seen NMOS) rewritten; 'Ea' printed without subscript | `ltc2975-p18-*`, `ltc2975-p20-*` | medium, low |
| 24 | Figures 6-14: '16-bit bus sequence' (numbers are field widths); the acknowledge before P in Figures 9-14 is drawn as NACK; drawing numbers F06-F14 | `ltc2975-p24-fig*` | medium, low |
| 39, 40, 42 | Figure 15 (one LTC2975 + MASTER/3 SLAVE DC/DCs, not five LTC2975s), Figure 16 (TOFF_DELAY from the CONTROL falling edge), Figure 17 (TRACK dividers fed from channel 0) rewritten | `ltc2975-p39-fig15-*`, `ltc2975-p40-fig16-*`, `ltc2975-p42-fig17-*` | medium |
| 55 | Figure 21 inductor thermal model: source/RC topology wrong; legend P_1/T_1 → P_I/T_I (letter I) | `ltc2975-p55-fig21-*` | medium |
| 75, 85-89 | Figure 22 (invented padlock / power-down step), Figures 23-25, 28 (350Ω inside the chip between V_IN_SNS and V_IN_SNS_CAP), 29 (TON_MAX from the V_OUT_EN edge), 30 (V_OUT_EN0, TON_DELAY0 after MFR_RESTART_DELAY) rewritten; p90 'I_OUT UC warning' | `ltc2975-p75-fig22-*`, `ltc2975-p8[5-9]-fig*`, `ltc2975-p90-*` | medium |
| 91-101, 108 | Figures 31 (LTC4210-1 hot-swap MOSFET vs S4010DS3 crowbar SCR), 32, 34, 35, 36, 40, 42, 43, 45 (screenshot: IIN not JIN, IOUT_UC_FAULT_LIMIT, TON_MAX_FAULT_RESP 0xB8) and the p108 typical application rewritten | `ltc2975-p9[1-9]-fig*`, `ltc2975-p10[01]-*`, `ltc2975-p108-*` | medium |
| 23, 62, 83 | Table 3 and p62 IOUT table empty columns; p83 table titles had replaced the real column headers | `ltc2975-p23-*`, `ltc2975-p62-*`, `ltc2975-p83-*` | low |
| many | Sub/superscripts and overbars as printed (I_OUT, V_IN, V_OUT, V_OUT_ENn subscripts added; full-size indices on p96/p100 and italic n in ASELn/FAULTBn/CONTROLn no longer subscripts); code backticks removed (p21, p86, p90); column-split paragraphs rejoined; heading levels and caption style per the conventions | `*-subscript*`, `*-heading*`, `*-caption*` | low |
| many | Manufacturer typos the conversion had silently corrected, put back as printed: 'IOUT_OC_FAULT_RESONSE', 'STATUS_MFR._SPECIFIC', 'N_TS max', 'Margin high (ignore faults and warnings' (no ')'), 'Mfr_ config _dac_mode', 'Mfr_config_ dac_pol', 'CONTROL0 ,', '0 =Do not pull', 'Ton_rise,Toff_delay', 'state,TON_RISE', 'IIN_CAL_ GAIN', 'MFR_FAULT_ LOG_RESTORE', '4paged', 'accumlate' | `*-as-printed` | low |

No content error found on p2, p3 (TOC, both columns), p19, p43, p50, p67, p71, p77-p78 (Tables 6/7), p105-p107; p25-p30 and p79-p83 had only caption/format fixes.
After the fixes: `validate.py --all` reports ltc2975 REVIEW as before; word/number coverage 99.0/99.5% → 99.3/99.6%. The 1 table issue is the p9 V_IH 'V_DD33 – 0.5' MIN (printed so). Geometry 155 / 0 / 5 / 1185 → 155 / 0 / 36 / 1150: the extra unverifiable rows are the p83 read-example tables, whose real column headers (restored) now bring them into the geometry scope; they hold byte numbers, not specifications. Other checks:
- `check_llm_fidelity.py`: ltc2975 0 spec-table failures (32 tables, 3371 cells), numeric subset True. The three p9 CONTROLn cells are written plain 'CONTROLn' (no `*n*` emphasis inside spec-table cells), otherwise the checker's word comparison fails on the emphasis markup.
- `relocate_images.py --check ltc2975`: OK (90 images). `check_struct_tables.py`: 82 tables, 535 rows, 0 misplaced fields.
- `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).

`ltc2975.llm.md` was regenerated with `tools/llm_compact.py ltc2975`. Every summary claim in `reports/llm/summaries/ltc2975.md` was re-checked against the corrected md (p1, p4-p10, p19): supply ranges and currents, 122µV/LSB, ±0.25%, ±170mV/±0.3%/±60µV, 10-bit DAC and 250µs update, ±0.6% and 85dB CMRR, 10-400kHz, 10,000 cycles / 20 years, packages and temperature ranges. None needed a change.

Not changed / open:
- Manufacturer errata kept as printed: p13 '2975 G12' printed twice (no G14); p21 'This will bring you great happiness.'; p25/p40/p61 truncated 'Mfr_track_en_chann'; p37 'back on..'; p44 'Mfr_track_en_chan0 = 1' under 'Slave channel n', 'programing'; p51 caption 'MFR_IOUT_CAL_GAIN_TC Data Contents' over the MFR_IIN_CAL_GAIN_TC table; p52 'PROPOGATE'; p55 'Value = Y • 2^14' (the example uses 2^-14); p56 'τINV = (θIS Cτ)' vs Eq4; p59 'MFR_WATCH_DOG_T'; p76 '300ms seconds'; p80 byte 104 hex '78'; p80-p82 Status_temperatureN / 'Read_in' / 'Status_temperature2' at bytes 122 and 180, and the read example's Status_temperatureN at preamble bytes 69/72/75/78 where Table 6 lists Status_mfr_specificN; p95 'due the current sense inputs'; p97 'can be be expressed'; Figure 46 'APERATURE'; p104 '9 .00 ±0.10'; the Figure 45 screenshot shows 'MFR_CONFIG_LTC2974'.
- Repo-wide conventions kept: straight apostrophes (the PDF prints ’, the md uses ' in ~75 places); hyphen-minus for some printed minus signs; LaTeX for formulas and some symbols; bold Features bullets not reproduced; Abs Max group labels ('Supply Voltages:') kept as `###`; nested `<sub>` for SENSEP<sub>n</sub>; italic `*n*` outside spec tables; '- 1)' list items on p48; REF PAGE cells are links on some pages and plain numbers on others; the p107 disclaimer and p108 copyright footer omitted.
- Doubts: p21 '### PMBus' kept H3 (bold 11.7pt, but the TOC lists it at the Device Address level); the Figure 41 description is incomplete but has no wrong facts; Figures 26/27/30/31-type curve descriptions give shapes only. Figure descriptions remain AI text, many rewritten from the drawings; read values from the image/PDF.

### sn74avc4t774 full page-by-page review (2026-10-26)

Scope: all 43 PDF pages of `sn74avc4t774.pdf`, reviewed one page at a time in the main session. Each page was checked as a rendered image (110 dpi page, 200 dpi halves, 300-500 dpi crops of the pinouts, the scope screenshot and drawing labels), as `pdftotext -layout` output and as PyMuPDF words/spans (positions, sizes, sub/superscripts), against the `{N-1}` section of `output/sn74avc4t774/sn74avc4t774.md`. A per-page word/number multiset diff flagged leftovers. Checked cell by cell: Package Information (p1), Pin Functions (p5), Abs Max/ESD/Recommended/Thermal (p6-p7), the EC table with both MIN/TYP/MAX groups (p8, x-centres under the column headers), the five switching-characteristics tables (p9-p11, all 60 rows compared in order with the PDF word rows; no value or column error), Tables 6-1/6-2/7-1/8-1, the packaging addendum (p21, 25 rows), tape-and-reel and box tables (p23-p24, 11 rows each) and the tube table (p25).
98 new fixes, all `sn74avc4t774-p*` ids in `fixes.json` (3 high, 12 medium, 83 low). Description fixes have two entries each (`-alt` / `-desc`). `replay_fixes.py` reproduces the md exactly.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 4 | Figure 4-4 RSV pinout had the PW/RGY numbering with DIR1/DIR2 swapped (md: pin 1 DIR2, 2 DIR1, 3 A1 ...); the PDF has 1-4 A1-A4, 5 DIR3, 6 DIR4, 7 OE, 8 GND, 9-12 B4-B1, 13 VCCB, 14 VCCA, 15 DIR1, 16 DIR2 (consistent with the RSV column of Table 4-1). Alt, pin table and description fixed; no pin-1 circle or thermal pad on RSV; BQB has no pin-1 circle; 'Not to scale' on DYY/RGY | `sn74avc4t774-p4-fig4-4-rsv-pinout-*`, `-p4-fig4-5-*`, `-p4-fig4-[23]-*` | high, low |
| 2, 16 | Typical application: the OE line has one dashed pullup to 1.8 V (no 'switch-like component to GND'); DIR3 to GND; A3/B3 carry SDO from the peripheral (A1-A4 are not all inputs); MCU on the 1.8 V rail, peripheral on 3.3 V; 0.1 µF caps | `-p2-typical-application-description`, `-p16-fig8-1-*` | medium |
| 14 | Figure 6-4 enable/disable description inverted (OE 'low to high (enable)', Output(1)/Output(2) starting levels, measurement points) | `-p14-fig6-4-enable-disable-description` | medium |
| 15 | Figure 7-1 logic diagram: invented OR gates; actually two AND gates (DIR1 & /OE, /DIR1 & /OE) enabling two 3-state inverting buffers | `-p15-fig7-1-logic-diagram-*` | medium |
| 17 | Figure 8-2 scope screenshot: the channel scales 2.00 V/2.00 V, 200ns, 2.50GS/s and trigger 1.16 V had been read as signal high/low levels | `-p17-fig8-2-scope-description-*` | medium |
| 18 | Figure 8-3 layout: OE has a pullup to a VCCA via (not 'to ground'), GND goes straight to a GND via, VCCA/VCCB have bypass capacitors (not resistors) | `-p18-fig8-3-layout-description-*` | medium |
| 12, 13 | Figure 5-1/5-2 curve descriptions (not linear; single-curve values) reduced to axes and curve order; Figure 6-1 load circuit (S1 has 3 positions, two RL); Figures 6-2/6-3 labels | `-p12-fig5-*`, `-p13-fig6-*` | low |
| 26-42 | Package drawings: RSV/BQB generic views (bottom view, pads not leads, no '4x4 grid'), outlines RSV0016A, PW0016A, RGY, BQB0016A, DYY0016A (DYY described as '4-pin', 1.6 mm pitch; body vs index-area dimensions, position vs profile tolerances, min/max given as 'reference'), land patterns, solder mask details (blue = metal, green = mask opening; colors were swapped) and stencils (pad length/width/pitch meanings, pin numbering) rewritten from the drawings | `-p2[5-9]-*`, `-p3[0-9]-*`, `-p4[0-2]-*` | medium (p33, p37, p40 outlines), low |
| 6, 8, 9-11 | As printed: Abs Max symbols are full-size in the PDF (VCCA, VI, IIK, Tstg, 'VI< 0'); EC I_OZ second 'VI' full-size; ROC 'VCCI' (md had 'VCCi'); switching headings 'VCCA = 1.2V ± 0.1V' without subscript (as in the TOC) | `-p6-absmax-symbols-*`, `-p6-roc-vcci-*`, `-p8-ec-ioz-*`, `-p9..p11-heading-*` | low |
| 1, 15, 16, 28-42 | 'RSV, (UQFN, 16)' as printed; column-split paragraph rejoined (p1); Table 7-1/8-1 captions bold; missing title blocks (EXAMPLE BOARD LAYOUT / STENCIL DESIGN, MECHANICAL DATA, THERMAL PAD MECHANICAL DATA, LAND PATTERN DATA) and drawing number 4231225/A, 4226161/A; RGY notes lettered A-G / A-F (the drawings refer to Note C-F); numbered notes that had become bullets | `-p1-*`, `-p15-table7-1-*`, `-p16-table8-1-*`, `*-title-block`, `*-notes-*` | low |

No content error found on p3 (TOC), p5 (Pin Functions), p7 (ROC continued, Thermal), p8 values/columns (the batch-3 p8 fixes still hold), p9-p11 values, p19, p20, p21-p24 and p43.
After the fixes: `validate.py --all` reports sn74avc4t774 REVIEW as before (the only flags are p33-p35, raster drawings with no extractable PDF text); word/number coverage 94.4/87.8% → 95.4/90.8%, text-loss pages 2 → 0, geometry 112 / 0 / 19 / 149 → 118 / 0 / 13 / 149. Other checks:
- `check_llm_fidelity.py`: sn74avc4t774 0 spec-table failures (12 tables, 1300 cells), numeric subset True (extra token '271' from the SLUA271 links, as before).
- `relocate_images.py --check sn74avc4t774`: OK (44 images). `check_struct_tables.py`: 1 table, 17 rows (ok 16, loose 1), 0 misplaced fields.
- `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).

`sn74avc4t774.llm.md` was regenerated with `tools/llm_compact.py sn74avc4t774`. Every summary claim in `reports/llm/summaries/sn74avc4t774.md` was re-checked against the corrected md (p1, p7, p8, p11, p15, p16): supply range, 4.6V tolerance, data rates, t_PLH/t_PHL at V_CCA = V_CCB = 3.3V (0.1-2.9 ns A to B, 0.1-2.8 ns B to A), 16 µA I_CCA + I_CCB, I_off ±0.1 typ / ±5 max, ±12 mA drive, packages and sizes, DIR/OE function. None needed a change.

Not changed / open:
- Manufacturer errata kept as printed: p1 'RSV, (UQFN, 16)', 'ensuring that they these inputs'; p7 'Y_JT'/'Y_JB' (Ψ printed as Y); p13-p14 notes lettered A.-F. while the drawings cite (1)-(6); p15 'voltage level translation', 'are support by'; p16 'when the device translate signal'; p33 'SEPRATE SHEET'; p38 note list headed '1. NOTES: (continued)'.
- Invisible 0.5 pt text in the PDF text layer ('SCALE 5.000' p27, 'SCALE 2.500' and 'A 20' p30, '15.000' p31) is not transcribed.
- The Figure 6-3 slope label renders as '500 ps/V – 1 s/V' but the text layer maps the glyph to '±'; the description follows the rendering.
- Repo-wide conventions kept: hyphen-minus for some printed minus signs and µ/μ as converted; straight apostrophes/quotes; LaTeX for some symbols in descriptions; running headers/footers, 'Submit Document Feedback', the p1 'IMPORTANT NOTICE' footer and the repeated p43 header omitted; `#### **TAPE AND REEL INFORMATION**` heading markup as in ina190; the Datalab alt-text line repeated after each figure description.
- Figure descriptions remain AI text. The package/land-pattern/stencil descriptions were rewritten from the drawings; curve descriptions give shapes only. Read values from the image/PDF.

### tps22990 full page-by-page review (2026-10-26)

Scope: all 34 PDF pages of `tps22990.pdf`, reviewed one page at a time in the main session. Each page was checked as a rendered image (110 dpi page, 200 dpi halves, 220-250 dpi crops of the schematics, block diagram, timing diagram, scope captures, layout and package drawings), as `pdftotext -layout` output and as PyMuPDF spans (fonts, sizes, glyphs such as ψ, invisible text), against the `{N-1}` section of `output/tps22990/tps22990.md`. A per-page word/number multiset diff flagged leftovers. Checked cell by cell: Device Comparison and Pin Functions (p3), Abs Max/ESD/ROC (p4), Thermal and both EC tables (p5-p7, every MIN/TYP/MAX/UNIT position), the 42 switching rows (p7-p8, in order against the PDF rows), Tables 1-4 (p17, p18, p23), packaging, tape-and-reel and box tables (p27-p30).
96 new fixes, all `tps22990-p*` ids in `fixes.json` (0 high, 16 medium, 80 low). Description fixes have two entries each (`-alt` / `-desc`). `replay_fixes.py` reproduces the md exactly. No EC, switching or table value was wrong; the earlier `tps22990-p5-isd-vin-columns` and `-p3-pins-9-10-vout` fixes still hold.

| Page(s) | Finding | Fix ids (prefix) | Severity |
|---|---|---|---|
| 1, 15, 21, 22 | Schematic descriptions wrong: Typical Application (VIN and VBIAS tied, C_IN missing, R_PU pulls PG up to VOUT, not the supply rail); Figure 34 test circuit and Figure 38 (separate VBIAS supply, R_PU from VOUT to PG, C_L/R_L in parallel on VOUT; the AI text grounded PG and put R_PU in series with the load); Figure 36 power sequencing (one common VBIAS supply, bottom PG not wired back to the top ON, CT is not current sense); Figure 37 (VBIAS not tied to the MCU, PG tied to GND) | `tps22990-p1-typical-application-description`, `-p15-fig34-description`, `-p21-fig36-*`, `-p22-fig3[78]-*` | medium |
| 15, 16 | Figure 35 timing definitions (t_ON/t_OFF are V_ON 50% to V_OUT 50%, t_D to V_OUT 10%); block diagram (VIN to the pass-FET drain, VOUT its source; VBIAS only feeds the charge pump; CT on the gate node; QOD FET from VOUT to GND, not tied to CT) | `-p15-fig35-description`, `-p16-block-diagram-*` | medium |
| 13, 14, 24 | Scope captures: channels are 1 ON, 2 VIN, 3 VOUT, 4 PG (the AI text listed 'VIN, IN, VOUT, PG'); Figure 30 is captioned 'Turnon Response' but shows a turnoff; Figures 39/40 have 2 = IOUT, 4 = PG (swapped), and the '200mA'/'100mA' peaks and '79.77µs'/'297µs' times were the channel scale and trigger position | `-p13-fig2[6-9]-*`, `-p13-fig30-*`, `-p14-fig3[123]-*`, `-p24-fig39-*`, `-p24-fig40-*` | low, medium |
| 31-33 | DML0010A outline (pin number '10' read as a 10 mm length, standoff/terminal thickness, min/max pairs, tolerance frames), land pattern (dimensions all called 'package width/height'; pads 8-10 are one comb-shaped SMD pad) and stencil (a solder paste example with the thermal pad split into two 1.038 × 1.148 apertures, not a solder mask drawing) rewritten from the drawings; missing p31 title block | `-p31-outline-description`, `-p31-title-block`, `-p32-land-pattern-*`, `-p33-stencil-*` | medium, low |
| 9-13 | The test conditions printed under Figures 1-11 and 13-30 (e.g. 'VON = 5 V, IOUT = 0 A, VIN = VBIAS') were only inside the AI descriptions; added as page text before each caption (p12 already had them) | `-p9..p13-fig*-conditions-missing` | low |
| 1, 3, 25 | 85°C curve is gray, not green; pinout description now names every pin; Figure 41 layout (one VOUT bypass capacitor, R_PU from PG to the VOUT copper, CT/VBIAS capacitors to a shared ground area) | `-p1-ron-vs-vin-colors`, `-p3-pinout-description`, `-p25-fig41-*` | low |
| 13 | Figure 25: the four V_BIAS curves overlap and the 2.5/3.3 V curves stop at lower V_IN (the AI text said rise time is higher for higher V_BIAS) | `-p13-fig25-*` | low |
| 4, 5, 17, 19 | As printed: ROC V_OUT MAX 'VIN' full-size; lowercase ψ_JT/ψ_JB (md had Ψ); Table 1 'CL = 0.1 uF, CIN = 1 uF' with a plain u; Equation 2 with '*'; full-size VIN/VBIAS/VOUT/IMAX in running text | `-p4-roc-vout-max-vin-as-printed`, `-p5-thermal-psi-lowercase`, `-p17-*`, `-p19-imax-*` | low |
| 6, 7 | Empty trailing column in the 3.3-V EC table and empty third column in the 5-V switching table removed; 'VHYS,ON'/'VPG,OL' without a space | `-p6-ec33-empty-column-symbols`, `-p7-switching-empty-column` | low |
| 7-24 | Equation numbers (1), (2), (3), (4), (5), (8) had become 'where' bullets or bullet suffixes; heading markup/levels (`**` inside headings, H4 '(continued)' titles, '## Application Information (continued)'); escaped LaTeX in the p19 link text; Figure 39/40 captions bold | `*-eq*-number*`, `*-heading-*`, `-p19-ec-link-text`, `-p24-fig*-caption-bold` | low |

No content error found on p2 (TOC, revision history), p8 (switching continued), p18 (Table 2, Table 3), p26, p27-p30 (packaging, tape and reel, box tables) or p34.
After the fixes: `validate.py --all` reports tps22990 OK (was REVIEW): word/number coverage 98.3/93.0% → 98.8/94.2%, low-coverage pages 1 → 0, geometry 128 / 0 / 9 / 74 unchanged, 0 table issues. The remaining number misses are tokenizer artifacts (LaTeX-wrapped V_BIAS/V_IN, the vector graph axis labels concatenated in the PDF text layer, the equation glyphs) and the omitted running headers/footers. Other checks:
- `check_llm_fidelity.py`: tps22990 0 spec-table failures (13 tables, 628 cells), numeric subset True (extra token '271' from the SLUA271 link, as before).
- `relocate_images.py --check tps22990`: OK (63 images). `check_struct_tables.py`: 1 table, 12 rows, all ok.
- `unittest` test_validate / test_llm_compact / test_struct_tables: OK (64 tests).

`tps22990.llm.md` was regenerated with `tools/llm_compact.py tps22990`. Every summary claim in `reports/llm/summaries/tps22990.md` was re-checked against the corrected md (p1, p3-p7, p16-p18, p20, p21): V_BIAS/V_IN ranges, 3.9/4.8/6 mΩ R_ON, 10 A, 63/77 µA and 5.5/7 µA bias currents, 34 µs turn-on and 31 µs rise time, 218/253 Ω R_PD, 1.2 V / 0.5 V ON thresholds, 25 V CT capacitor rating, 1 µF C_IN, package and temperature range. None needed a change.

Not changed / open:
- Manufacturer errata kept as printed: p13 Figure 30 captioned 'Turnon Response' although it shows a turnoff; p24 'Figure 39. . Inrush Current'; p12 'Figure 23. PG Turnoff vs Input Voltage' (no 'Time'); p18 'Typical PG turnon time (us)'; p16 'end equipment' vs p1 'end equipments'.
- 'TA = 25ºC' in the switching-table group rows is printed with a masculine ordinal º; the md keeps °. 'CIN= 1 µF' (no space) is written 'C_IN = 1 µF'.
- The p11 Figure 13/14 axis label prints 'Turnon Time (us)'; the descriptions say µs.
- Invisible 0.79-pt 'SCALE 4.500' on p31 is not transcribed. The 'IMPORTANT NOTICE' footer label on p34, running headers/footers, 'PACKAGE OPTION ADDENDUM'/'PACKAGE MATERIALS INFORMATION' page headers and dates are omitted as in the other datasheets.
- Repo-wide conventions kept: hyphen-minus for printed minus signs inside LaTeX table cells, LaTeX for symbols, `- (1)` footnotes after the Abs Max/ROC tables, the Device Information and Pin Functions merged cells written as separate rows, the p12 condition lines in LaTeX while the added ones use `<sub>`.
- Figure descriptions remain AI text; the schematics, block diagram, timing diagram, scope captures and package drawings were rewritten from the drawings, curve descriptions give shapes and curve order only. Read values from the image/PDF.
