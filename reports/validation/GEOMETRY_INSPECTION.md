# Geometry sample review

The review used PDF word coordinates and rendered page images, comparing the
current Markdown rows to the PDF columns. Only stdlib and PyMuPDF were used.

- **TPS22990 p6–7:** initial shutdown-current matches incorrectly selected the
  output pull-down resistance row (218/253 Ω). Initial on-resistance continuation
  matches selected a neighboring temperature row (MAX 5.7 instead of 4.8).
  Require the most specific local condition, including every numeric condition
  token; ambiguous repetitions abstain. The checked shutdown and on-resistance
  controls now have no geometry findings.
- **TPS63802 p6–7:** literal percent unit cells were initially treated as missing
  after unit normalization stripped the percent sign. Equal normalized units now
  compare equal even when both normalize to an empty string. The printed percent
  units remain present in Markdown and are not flagged.
- **LTC2975 p6–7:** the image confirms the full-scale DAC limits at MIN 1.3,
  TYP 1.38, MAX 1.44 V (and 2.5/2.65/2.77 V). Markdown puts the bullet in MIN,
  moves the numbers right, and merges the maximum with UNIT. These flags remain.
  `% of Reading` versus a PDF value carrying `%` with `of Reading` in UNIT is a
  typography difference, now normalized. Unrelated register/bit tables cannot
  inherit a specification schema from an earlier table on the page.
- **MAX31730 p2–3:** initial remote/local accuracy matches selected the wrong
  temperature condition, producing fictitious missing ±2/±1.5 limits. Require
  the complete local condition; unresolved wrapped conditions abstain. The
  reviewed current accuracy rows now have no geometry findings.
- **LT1965FB p4:** a supplementary check found repeated `ILOAD = 1mA` baselines
  distinguished by a temperature bullet. A shared, centered parameter biased the
  match to the second row. Adjacent candidates with identical qualifying
  conditions now abstain, and the dropout-voltage control is not flagged.

Frozen LTC3315A and INA190 regression rows retain all confirmed errors even if
output Markdown is later repaired. Current-file controls assert that NMOS
Current Limit, INA190 Supply voltage, and CMRR are actually verified OK, rather
than merely escaping a finding. Other ambiguity/typography controls may be
unverifiable. An OK datasheet status does not certify unverifiable rows.
