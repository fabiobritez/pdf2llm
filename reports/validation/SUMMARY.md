# Datasheet validation summary

Means use unique normalized token sets after margin, recurring-line and figure removal.
Text loss: words < 90% with ≥8 missing, or numbers < 90% with ≥3 missing. BAD: ≥20% text-loss pages (minimum 3), or ≥8 high-confidence table rows.

Geometry rows count numeric data rows: verified OK / mismatched / unverifiable. Ambiguous row matches and unsupported table layouts are unverifiable; OK is not certification of those rows.

| Datasheet | Pages | Mean words | Mean numbers | Low text pages | Missing unit | Wrong column | Column shift | Ordering | Ragged | Geometry column | Geometry missing | Geometry rows OK / mismatch / unverifiable / out of scope | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [ad5593r](ad5593r.md) | 47 | 99.9% | 99.8% | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 132 / 0 / 5 / 262 | OK |
