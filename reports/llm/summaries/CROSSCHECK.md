# Summary cross-check log

## ina190

Drafted by agy from the compact datasheet text; checked claim by claim by codex (1 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

- fix: Voltage output, reference (REF), and enable (ENABLE) pins; UQFN, SC70, and SOT-23 packages specified from -40°C to +125°C [p1]. -> Voltage output and reference (REF) pins; ENABLE is available only in SOT-23 (DDF) and UQFN (RSW) packages. UQFN, SC70, and SOT-23 packages are specified from -40°C to +125°C [p1, p3].

## lt1965fb

Drafted by agy from the compact datasheet text; checked claim by claim by codex (4 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

- fix: GND pin current (0mA load) is 0.5mA typ, 1.1mA max; output noise is 40 μV_RMS typ (10Hz to 100kHz). [p4] -> For the adjustable version at 0mA load and V_IN = V_OUT(NOMINAL) + 1V, GND pin current is 0.5mA typ, 1.1mA max; fixed versions typically add 100µA. Output noise is 40μV_RMS typ at 25°C with C_OUT = 10
- fix: Shutdown quiescent current is 0.01µA typ, 1µA max; 120Hz ripple rejection is 57dB min, 75dB typ. [p5] -> At 25°C, shutdown quiescent current is 0.01µA typ, 1µA max with V_IN = 6V and V_SHDN = 0V; ripple rejection is 57dB min, 75dB typ at 120Hz with V_IN − V_OUT = 1.5V average, 0.5V_P-P input ripple, and 
- fix: Two external resistors set adjustable V_OUT (R1 < 12.1k recommended); stability requires a minimum 10μF output capacitor with ESR of 0.3Ω or less. [p12] -> Two external resistors set adjustable V_OUT (R1 < 12.1kΩ recommended); a minimum 10μF output capacitor with ESR of 0.3Ω or less is recommended to prevent oscillations. [p12]
- fix: Pulling /SHDN low turns off the output for shutdown; drive with logic or open collector/drain, or tie to V_IN if unused. [p11] -> Pulling /SHDN low turns off the output for shutdown; drive with logic or an open collector/drain with a pull-up resistor, or tie to V_IN if unused. [p11]

## ltc3309a

Drafted by agy from the compact datasheet text; checked claim by claim by codex (3 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

- fix: Internal switches with 31mΩ typ PMOS and 8mΩ typ NMOS ON-resistance, 22ns typ (42ns max) minimum on-time, and 100% min maximum duty cycle [p1, p3]. -> Internal switches have 31mΩ typ PMOS and 8mΩ typ NMOS ON-resistance at V_IN = 3.3V and T_A = 25°C; minimum on-time is 22ns typ (42ns max) at V_IN = 5.5V over the specified junction temperature range; 
- fix: Quiescent current of 40μA typ (60μA max) sleeping in Burst Mode, 1.2mA typ (2mA max) not sleeping, and 1μA typ (2μA max) in shutdown [p3]. -> At T_A = 25°C and V_IN = 3.3V, quiescent current is 40μA typ (60μA max) sleeping in Burst Mode and 1.2mA typ (2mA max) in all modes while not sleeping, excluding switching currents; shutdown current i
- fix: AEC-Q100 qualified 12-lead 2mm × 2mm × 0.74mm LQFN package; -40°C to +125°C, -40°C to +150°C, and -55°C to +150°C junction temperature grades [p1, p2]. -> Available in a 12-lead 2mm × 2mm × 0.74mm LQFN package with -40°C to +125°C, -40°C to +150°C, and -55°C to +150°C operating junction temperature grades. AEC-Q100 automotive versions are available as t
