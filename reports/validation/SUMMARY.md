# Datasheet validation summary

Means use unique normalized token sets after margin, recurring-line and figure removal.
Text loss: words < 90% with ≥8 missing, or numbers < 90% with ≥3 missing. BAD: ≥20% text-loss pages (minimum 3), or ≥8 high-confidence table rows.

Geometry rows count numeric data rows: verified OK / mismatched / unverifiable. Ambiguous row matches and unsupported table layouts are unverifiable; OK is not certification of those rows.

| Datasheet | Pages | Mean words | Mean numbers | Low text pages | Missing unit | Wrong column | Column shift | Ordering | Ragged | Geometry column | Geometry missing | Geometry rows OK / mismatch / unverifiable | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [ad5593r](ad5593r.md) | 47 | 99.9% | 99.8% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 108 / 0 / 291 | OK |
| [ad5711r-ad5710r](ad5711r-ad5710r.md) | 60 | 98.1% | 98.0% | 2 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 122 / 0 / 302 | REVIEW |
| [ina190](ina190.md) | 47 | 94.6% | 93.4% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 57 / 0 / 159 | OK |
| [lt1965fb](lt1965fb.md) | 22 | 99.5% | 99.2% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 55 / 0 / 161 | OK |
| [ltc2975](ltc2975.md) | 108 | 98.8% | 99.5% | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 126 / 0 / 1252 | REVIEW |
| [ltc3309a](ltc3309a.md) | 26 | 99.9% | 100.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 37 / 0 / 138 | OK |
| [ltc3313](ltc3313.md) | 29 | 99.7% | 100.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 42 / 0 / 124 | OK |
| [ltc3315a](ltc3315a.md) | 26 | 99.8% | 99.8% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 37 / 0 / 98 | OK |
| [max31730](max31730.md) | 48 | 99.9% | 100.0% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 37 / 0 / 346 | OK |
| [sn74avc4t774](sn74avc4t774.md) | 43 | 94.4% | 87.8% | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 23 / 0 / 276 | REVIEW |
| [tps22990](tps22990.md) | 34 | 98.3% | 93.0% | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 71 / 0 / 165 | REVIEW |
| [tps6287b20](tps6287b20.md) | 74 | 94.8% | 93.0% | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 151 / 0 / 351 | REVIEW |
| [tps63070](tps63070.md) | 42 | 96.9% | 91.8% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 67 / 0 / 141 | OK |
| [tps63802](tps63802.md) | 38 | 95.7% | 92.7% | 1 | 0 | 4 | 4 | 0 | 0 | 0 | 0 | 46 / 0 / 101 | REVIEW |
| [ts3a5018](ts3a5018.md) | 41 | 95.6% | 91.3% | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 76 / 0 / 146 | REVIEW |
