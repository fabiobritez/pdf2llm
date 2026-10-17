# Manual inspection notes

Page numbers are 1-based. These ten pages have concrete omissions, checked
against PDF extraction and the complete normalized Markdown **including alt
text**. The first four lose specification text or captions; the last six lose
mechanical/land-pattern drawing dimensions. They are not ten confirmed prose
losses. Drawing omissions belong in figure comparison; detached callouts can
still escape the geometric regions and appear as text-loss candidates.

| Datasheet | Page | Missing information |
| --- | --- | --- |
| lt1965fb | 4 | Output/ADJ voltage maxima: 1.218, 1.523, 1.545, 1.827, 1.854, 2.538, 2.575, 3.35, 3.399. |
| ts3a5018 | 8 | Leakage/switching test conditions: VNC/VNO/VCOM settings, Open, Switch ON/OFF, Figure 18/19/21 references, RL=300 ohm and CL=35 pF. |
| ad5711r-ad5710r | 27 | Figure 57 caption describing MUX_OUT configuration for four devices with different device addresses. |
| tps6287b20 | 55 | Figure 10-26 caption: stacking two devices for up to 50 A; image also has empty alt text. |
| ts3a5018 | 35 | Package-outline dimensions including 0.069 and 4.81. |
| sn74avc4t774 | 40 | Package-outline dimensions including 4.3 and 3.5. |
| tps22990 | 31 | Package-outline dimensions including 0.56 and 0.19. |
| sn74avc4t774 | 30 | Package-outline dimensions including 2.5 and 4.3. |
| tps6287b20 | 72 | Land-pattern dimensions including 1.25 and 1.75. |
| tps63802 | 36 | Package drawing dimensions including 0.55 and 1.3 (page also contains a land-pattern drawing). |

INA190 pages 3, 5, 6 and 13–30 were reviewed: the initial low coverage largely
came from boilerplate and graphics. Low-count residuals such as D115/D030 graph
IDs are not substantial text loss. LTC3313 pages 12–17 and 23–24 likewise lose
most initial warnings after soft-hyphen and figure fixes. TPS63070 specification,
application and plot pages no longer trigger the earlier blanket low scores.

Table issue audit covered all eight sheets with original findings:

- AD5711R/AD5710R p5: headroom/footroom MIN>TYP stays review confidence.
- INA190 p4–5: actual condition/device selectors under MIN; Gain error still detected.
- LTC2975 p6–7: full-temperature bullet consumes MIN, shifting values; maxima such
  as 1.44 V and 200 uA merge into UNITS. These remain high confidence.
- LTC3315A p3: same merged maximum/unit pattern (3.5 A).
- TPS22990 p5: actual temperature conditions under MIN; its 36 shared-unit warnings removed.
- TPS6287B20 p7: actual condition text under MIN and 4.6 mA/450 uA merged into UNIT;
  p10 fSW±10% is legitimate symbolic content and is no longer flagged.
- TPS63802 p6: four on-resistance rows put a second condition under MIN.
- TS3A5018 p4: diode/clamp conditions under MIN and -50 mA merged into UNIT;
  p6–7 inline THD percentages are valid and are no longer flagged.

Known residual ambiguity: package-drawing labels outside the inferred region,
PDF font/reading-order fragments, compounds/variable spellings, source typos
corrected in Markdown, and unique-token scoring hiding repeated-cell losses.
Blank PDF text pages are extraction limitations, not measured omissions.
