# Datasheet validation summary

Means use unique normalized token sets after margin, recurring-line and figure removal.
Text loss: words < 90% with ≥8 missing, or numbers < 90% with ≥3 missing. BAD: ≥20% text-loss pages (minimum 3), or ≥8 high-confidence table rows.

Geometry rows count numeric data rows: verified OK / mismatched / unverifiable. Ambiguous row matches and unsupported table layouts are unverifiable; OK is not certification of those rows.

| Datasheet | Pages | Mean words | Mean numbers | Low text pages | Missing unit | Wrong column | Column shift | Ordering | Ragged | Geometry column | Geometry missing | Geometry rows OK / mismatch / unverifiable / out of scope | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [ad5593r](ad5593r.md) | 47 | 100.0% | 99.8% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 132 / 0 / 5 / 242 | OK |
| [ad5711r-ad5710r](ad5711r-ad5710r.md) | 60 | 99.9% | 100.0% | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 155 / 0 / 15 / 247 | REVIEW |
| [ina190](ina190.md) | 47 | 94.8% | 94.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 57 / 0 / 1 / 150 | OK |
| [lt1965fb](lt1965fb.md) | 22 | 99.9% | 100.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 63 / 0 / 0 / 66 | OK |
| [ltc2975](ltc2975.md) | 108 | 99.0% | 99.5% | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 155 / 0 / 5 / 1185 | REVIEW |
| [ltc3309a](ltc3309a.md) | 26 | 99.9% | 100.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 37 / 0 / 1 / 91 | OK |
| [ltc3313](ltc3313.md) | 29 | 99.7% | 100.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 44 / 0 / 0 / 45 | OK |
| [ltc3315a](ltc3315a.md) | 26 | 99.8% | 100.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 37 / 0 / 13 / 37 | OK |
| [max31730](max31730.md) | 48 | 99.9% | 100.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 42 / 0 / 8 / 333 | OK |
| [sn74avc4t774](sn74avc4t774.md) | 43 | 94.4% | 87.8% | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 112 / 0 / 19 / 149 | REVIEW |
| [tps22990](tps22990.md) | 34 | 98.3% | 93.0% | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 128 / 0 / 9 / 74 | REVIEW |
| [tps6287b20](tps6287b20.md) | 74 | 95.3% | 93.7% | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 167 / 0 / 8 / 311 | REVIEW |
| [tps63070](tps63070.md) | 42 | 96.9% | 91.8% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 69 / 0 / 2 / 116 | OK |
| [tps63802](tps63802.md) | 38 | 95.7% | 92.7% | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 48 / 0 / 3 / 86 | REVIEW |
| [ts3a5018](ts3a5018.md) | 41 | 95.6% | 91.3% | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 124 / 0 / 1 / 96 | REVIEW |
