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


## ltc3315a

Drafted by agy from the compact datasheet text; checked claim by claim by codex (3 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

- fix: Oscillator frequency (f_SW) is 1.85MHz min, 2MHz typ, 2.15MHz max (1MHz min to 3MHz max sync); minimum on time is 25ns typ, 45ns max [p4]. -> Oscillator frequency (f_SW) is 1.85MHz min, 2MHz typ, 2.15MHz max (1MHz min to 3MHz max sync); minimum on time at V_IN = 5.5V is 25ns typ, 45ns max [p4].
- fix: V_IN quiescent current is 1.2μA typ, 2μA max in shutdown and 45μA typ, 70μA max (one buck sleeping, Burst Mode) [p3]. -> V_IN quiescent current is 1.2μA typ, 2μA max in shutdown and 45μA typ, 70μA max with only one buck enabled, in regulation and sleeping in Burst Mode (T_A = 25°C, V_IN = 3.3V) [p3].
- fix: Available in AEC-Q100 qualified 12-lead 2mm × 2mm × 0.74mm LQFN and 16-ball 1.64mm × 1.64mm × 0.5mm WLCSP packages [p1]. -> Available in 12-lead 2mm × 2mm × 0.74mm LQFN and 16-ball 1.64mm × 1.64mm × 0.5mm WLCSP packages [p1]. Automotive-qualified versions are the listed LQFN #W variants [p3].

## max31730

Drafted by agy from the compact datasheet text; checked claim by claim by codex (0 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

## ltc3313

Drafted by agy from the compact datasheet text; checked claim by claim by codex (5 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

- fix: Operating supply voltage (V_IN) from 2.25V min to 5.5V max, 1.3mA typ (2.0mA max) quiescent current, and 1μA typ (2μA max) shutdown current [p3]. -> Operating V_IN range is 2.25V to 5.5V. At T_A = 25°C and V_IN = 3.3V, quiescent current is 1.3mA typ (2.0mA max), excluding switching currents; shutdown current is 1μA typ (2μA max) with V_EN = 0.1V [
- fix: Internal switches with 8mΩ typ top and 3mΩ typ bottom ON-resistance; top switch current limit is 18A min, 21A typ, 24A max [p3]. -> Internal switches have 8mΩ typ top and 3mΩ typ bottom ON-resistance at T_A = 25°C and V_IN = 3.3V; the top switch current limit is 18A min, 21A typ, 24A max for V_OUT/V_IN ≤ 0.2 and current flowing ou
- fix: R_T-programmed switching frequency from 0.5MHz min to 5MHz max (2MHz typ default), 35ns typ (60ns max) minimum on-time, and 100% min maximum duty cycle [p3]. -> R_T-programmed switching frequency ranges from 0.5MHz to 5MHz; with RT tied to V_IN, the default frequency is 2MHz typ (1.8MHz min, 2.2MHz max). Minimum on-time is 35ns typ (60ns max), and maximum dut
- fix: Precision 0.4V typ EN rising threshold, PGOOD output, SSTT soft-start/tracking, 4mV/°C typ temperature monitor, and 0.5MHz min to 2.25MHz max synchronization [p -> Precision 0.4V typ EN rising threshold, PGOOD output, SSTT soft-start/tracking, 4mV/°C typ temperature monitor, and 0.5MHz to 2.25MHz external synchronization with RT tied to V_IN [p3, p16].
- fix: Supports multiphasing parallel converters for automotive (AEC-Q100 qualified), industrial, communications, server, telecom, POL, and FPGA/ASIC/μP core supplies  -> Supports multiphasing parallel converters and industrial, communications, server, telecom, POL, and FPGA/ASIC/μP core applications. AEC-Q100-qualified automotive versions use the #W suffix; only the l

## ad5593r

Drafted by agy from the compact datasheet text; checked claim by claim by codex (2 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

- fix: DAC: 12 Bits typ resolution, -1 LSB min to +1 LSB max INL and DNL [p3]. -> DAC: 12 Bits typ resolution; INL and DNL each -1 LSB min to +1 LSB max, with outputs unloaded and linearity calculated over codes 8 to 4085 [p3, p6].
- fix: DAC AC and reference: 6 μs typ settling time, 1.25 V/μs typ slew rate; V_REF 2.495 V min, 2.5 V typ, 2.505 V max [p4]. -> DAC AC and reference: 6 μs typ settling time for a ¼-to-¾-scale step, 1.25 V/μs typ slew rate; V_REF output 2.495 V min, 2.5 V typ, 2.505 V max [p4, p17].

## ad5711r-ad5710r

Drafted by agy from the compact datasheet text; checked claim by claim by codex (0 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

## ltc2975

Drafted by agy from the compact datasheet text; checked claim by claim by codex (3 issue(s)); numbers verified automatically by tools/check_llm_fidelity.py.

- fix: Operates from V_PWR (4.5V min to 15V max) or V_DD33 (3.13V min to 3.47V max), drawing 10mA typ (13mA max). [p5] -> Operates from V_PWR (4.5V min to 15V max, V_DD33 floating) or from V_DD33 tied to V_PWR (3.13V min to 3.47V max), drawing 10mA typ (13mA max). [p5]
- fix: Output current sensing (-170mV min to 170mV max) achieves ±0.3% of Reading max error; 10 Bits typ DACs update every 250µs typ. [p6] -> Output current sensing spans -170mV to 170mV differential, with ±0.3% of Reading max error for sense magnitudes of 20–170mV and ±60µV max for magnitudes ≤20mV; 10 Bits typ DACs update every 250µs typ 
- fix: Supports 10kHz min to 400kHz max PMBus clock and EEPROM with 10,000 Cycles min endurance and 20 Years min retention. [p9] -> Supports 10kHz min to 400kHz max PMBus clock. EEPROM endurance is 10,000 cycles min with writes at 0°C < T_J < 85°C; retention is 20 years min at T_J < 105°C for EEPROM cycled fewer than 10,000 times.
