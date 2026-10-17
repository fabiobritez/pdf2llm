# Unverifiable spec rows: two-model review (task 2b)

Rows that `validate.py` cannot match to PDF words (merged/wrapped cells, ordering tables) were sent, with the page image, to two reviewers:
codex `gpt-6.1-sol` (reasoning xhigh) and grok `grok-4.7` (agy `gemini-4-argon-high` was out of quota, 429 until ~2026-10-23).

| datasheet | page | rows | codex flagged | grok flagged | outcome |
|---|---|---|---|---|---|
| ad5593r | 3 | 2 | 0 | 0 | both: correct |
| ad5593r | 5 | 3 | 0 | 0 | both: correct |
| ad5711r-ad5710r | 4 | 6 | 0 | 0 | both: correct |
| ad5711r-ad5710r | 5 | 6 | 0 | 0 | both: correct |
| ad5711r-ad5710r | 7 | 2 | 1 | 0 | see notes |
| ad5711r-ad5710r | 8 | 3 | 0 | 0 | both: correct |
| ina190 | 6 | 1 | 0 | 0 | both: correct |
| ltc2975 | 5 | 4 | 0 | 0 | both: correct |
| ltc2975 | 8 | 1 | 0 | 0 | both: correct |
| ltc3309a | 3 | 1 | 0 | 0 | both: correct |
| ltc3315a | 3 | 13 | 0 | 0 | both: correct |
| max31730 | 2 | 8 | 1 | 0 | see notes |
| sn74avc4t774 | 6 | 12 | 0 | 0 | both: correct |
| sn74avc4t774 | 8 | 7 | 0 | 0 | both: correct |
| tps22990 | 6 | 6 | 0 | 0 | both: correct |
| tps22990 | 7 | 3 | 0 | 0 | both: correct |
| tps6287b20 | 6 | 4 | 0 | 0 | both: correct |
| tps6287b20 | 11 | 1 | 0 | 0 | both: correct |
| tps6287b20 | 12 | 3 | 0 | 0 | both: correct |
| tps63070 | 7 | 2 | 0 | 0 | both: correct |
| tps63802 | 6 | 2 | 0 | NOJSON | codex: correct; grok pending |
| ts3a5018 | 6 | 1 | 0 | pending | codex: correct; grok pending |

Total rows reviewed: 91.

Notes:
- max31730 p2 (codex): THERM overbar -> fixed for the whole datasheet (fixes.json `max31730-*-therm-overbar`).
- ad5711r-ad5710r p7 L329 (codex): the PDF literally prints 'ixternal reference' (vendor typo; context = internal reference). md keeps 'internal'; left for manual decision.
- Rows marked pending were only reviewed by codex; grok/agy second opinion still to do.
