# Frozen regression geometry findings

These findings use the broken snippets in tools/test_validate.py against the repository PDFs, not the now-repaired output Markdown. MD lines below refer to the original broken files observed at the start of this task; fixture_line in JSON identifies the frozen snippet line. Current results are in SUMMARY.md.

| Datasheet | Page | Original MD line | Parameter | Value | MD column | PDF column | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ltc3315a | 3 | 167 | PMOS Current Limit (ILIM ) / Current out of SW, VOUT /VIN <= 0.2 | 2.9 | TYP | MIN | high |
| ltc3315a | 3 | 167 | PMOS Current Limit (ILIM ) / Current out of SW, VOUT /VIN <= 0.2 | 3.2 | MAX | TYP | high |
| ltc3315a | 3 | 167 | PMOS Current Limit (ILIM ) / Current out of SW, VOUT /VIN <= 0.2 | 3.5 | UNIT | MAX | high |
| ltc3315a | 4 | 182 | Maximum Duty Cycle | 100 | TYP | MIN | high |
| ltc3315a | 4 | 194 | PGOOD Delay | 120 | MIN | TYP | high |
| ltc3315a | 4 | 196 | PGOOD PullDown Resistance / VPGOOD = 0.1V | 10 | MIN | TYP | high |
| ltc3315a | 4 | 196 | PGOOD PullDown Resistance / VPGOOD = 0.1V | 20 | TYP | MAX | high |
| ltc3315a | 4 | 208 | MODE/SYNC No Clock Detect Time | 10 | MIN | TYP | high |
| ina190 | 4 | 196 | VIN+ , VIN- / Analog inputs | Differential (VIN+ ) - (VIN- )(2) | MIN | CONDITIONS | high |
| ina190 | 4 | 196 | VIN+ , VIN- / Analog inputs | -42 | MAX | MIN | high |
| ina190 | 4 | 196 | VIN+ , VIN- / Analog inputs | 42 | MISSING | MAX | high |
| ina190 | 4 | 197 | VIN+ , VIN- , with respect to GND(3) | VIN+ , VIN- , with respect to GND(3) | MIN | CONDITIONS | high |
| ina190 | 4 | 197 | VIN+ , VIN- , with respect to GND(3) | GND – 0.3 | MISSING | MIN | high |
| ina190 | 4 | 213 | V(ESD) / Electrostatic discharge | Humanbody model (HBM), per ANSI/ESDA/JEDEC JS-001(1) | VALUE | CONDITIONS | high |
| ina190 | 4 | 213 | V(ESD) / Electrostatic discharge | +-3000 | UNIT | VALUE | high |
| ina190 | 4 | 214 | Chargeddevice model (CDM), per JEDEC specification JESD22-C101(2) | Chargeddevice model (CDM), per JEDEC specification JESD22-C101(2) | VALUE | CONDITIONS | high |
| ina190 | 4 | 214 | Chargeddevice model (CDM), per JEDEC specification JESD22-C101(2) | +-1000 | UNIT | VALUE | high |
| ina190 | 5 | 267 | EG / Gain error / VOUT = 0.1 V to VS -0.1 V | A1 devices | MIN | CONDITIONS | high |
| ina190 | 5 | 272 | RVRR / Reference voltage rejection ratio / VREF = 100 mV to VS -100 mV , TA = -40degC to +125degC | A1 devices | MIN | CONDITIONS | high |
| ina190 | 5 | 280 | VZL / Zero current output voltage / VS = 1.8 V , RL = 10 komega to GND, TA = -40degC to +125degC , VSENSE = 0 mV , VREF = 0 V | A1, A2, A3 devices | MIN | CONDITIONS | high |
