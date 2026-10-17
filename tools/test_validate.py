"""Offline regression checks: python -m unittest tools.test_validate."""
import unittest
try:
    from tools import validate as v
except ModuleNotFoundError:
    import validate as v
import pymupdf


class ValidatorTests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(v.tokens('ﬁlter ﬂow volt-\nage soft\u00adhyphen'),
                         v.tokens('filter flow voltage softhyphen'))
        self.assertEqual(v.normalize(r'V_{\mathrm{IN}}'), v.normalize('V<sub>IN</sub>'))
        self.assertEqual(v.tokens(r'\Delta ≤ ≥ ≈ ~ \leq \geq \approx \sim \cdot'),
                         v.tokens('Δ <= >= ~ ~ <= >= ~ ~ *'))
        self.assertEqual(v.tokens('± 1.00% −2'), v.tokens(r'\pm1% -2'))

    def test_soft_hyphen_and_compounds(self):
        self.assertEqual(v.tokens('capaci\u00ad\ntor common-\nmode 0 . 434'),
                         v.tokens('capacitor common-mode 0.434'))

    def test_repeated_lines(self):
        doc = pymupdf.open()
        for number in range(5):
            page = doc.new_page()
            page.insert_text((70, 100), f'Document revision {number}')
            page.insert_text((70, 200), ['alpha', 'bravo', 'charlie', 'delta', 'echo'][number])
        result = v.extract_document(doc)
        self.assertTrue(all(p['removed']['repeated']['words'] == 2 for p in result))
        self.assertTrue(all('Document' not in p['text'] for p in result))
        doc.close()

    def test_ina_gain_shift_and_inline_percent(self):
        text = '| PARAMETER | | CONDITIONS | MIN | TYP | MAX | UNIT |\n'
        text += '| EG | Gain error | VOUT = 0.1 V | A1 devices | -0.04% | ±0.2% | |\n'
        issues = v.table_issues(text)
        self.assertTrue(any(i['type'] == 'column shift' and i['confidence'] == 'high' for i in issues))
        self.assertFalse(any(i['type'] == 'missing unit' for i in issues))
        self.assertFalse(v.table_issues('| PARAMETER | MIN | TYP | MAX | UNIT |\n| Error | | 0.1% | ±0.2% | |'))

    def test_uppercase_line_join(self):
        self.assertEqual(v.tokens("OUTPUT_CON-\nTROL"), v.tokens("OUTPUT_CONTROL"))

    def test_sentence_period_does_not_join_numbers(self):
        self.assertEqual(v.numbers(v.normalize('Channel 0.\n01: disabled')), {'0', '1'})

    def test_percent_unit_cell_and_dotted_leaders(self):
        self.assertEqual(v.tokens('limit ....–40°C ±0.75 | % of Reading'),
                         v.tokens('limit -40°C ±0.75% of Reading'))

    def test_subscript_preserves_following_prose(self):
        self.assertEqual(v.tokens('V <sub>IN</sub> must exceed V<sub>ON</sub> voltage'),
                         v.tokens(r'V_{IN} must exceed V_{ON} voltage'))

    def test_frequency_relative_percent_is_symbolic(self):
        self.assertTrue(v.symbolic(v.normalize(r'$f_{SW}-10\%$')))
        self.assertFalse(v.table_issues('| PARAMETER | MIN | TYP | MAX | UNIT |\n'
                                       r'| Spread | $f_{SW}-10\%$ | $f_{SW}+10\%$ | | |'))

    def test_shared_tps_units(self):
        text = '| PARAMETER | TEST CONDITIONS | | TA | MIN | TYP | MAX | UNIT |\n'
        text += '| RON | IOUT = -200 mA | VIN = 5 V | 25°C | | 3.9 | 4.8 | mΩ |\n'
        text += '| | | VIN = 2.5 V | 25°C | | 3.9 | 4.8 | |\n'
        self.assertFalse(v.table_issues(text))

    def test_ltc_merged_max_unit_is_real(self):
        text = '| SYMBOL | PARAMETER | CONDITIONS | MIN | TYP | MAX | UNITS |\n'
        text += '| VFS | Full scale | Gain 0 | ● | 1.3 | 1.38 | 1.44 V |'
        self.assertTrue(any(i['type'] == 'unit in wrong column' for i in v.table_issues(text)))

    def test_table_not_figure_and_margin_removal(self):
        doc = pymupdf.open()
        page = doc.new_page(width=600, height=800)
        page.insert_text((60, 25), 'Copyright 2020')
        page.insert_text((60, 120), 'MIN')
        page.insert_text((130, 120), 'MAX')
        page.insert_text((60, 150), 'voltage 12')
        page.draw_rect(pymupdf.Rect(50, 95, 200, 180))
        page.draw_rect(pymupdf.Rect(300, 300, 500, 500))
        page.insert_text((350, 350), 'axis 99')
        result = v.extract_document(doc)[0]
        self.assertIn('voltage', result['text'])
        self.assertNotIn('Copyright', result['text'])
        self.assertIn('axis', result['figure'])
        self.assertGreater(result['removed']['margin']['numbers'], 0)
        doc.close()

# Frozen broken Markdown: PDFs and correct controls are read from the repository,
# but repairs to output/*.md must not remove the regression cases.
LTC_P3 = r'''| PARAMETER | CONDITIONS | MIN | TYP | MAX | UNITS |
| PMOS Current Limit (I <sub>LIM</sub> ) | Current out of SW, V <sub>OUT</sub> /V <sub>IN</sub> ≤ 0.2 | | 2.9 | 3.2 | 3.5 A |'''
LTC_P4 = r'''| PARAMETER | CONDITIONS | MIN | TYP | MAX | UNITS |
| Maximum Duty Cycle | | ● | 100 | | % |

### Power Good/Soft-Start

| | | | | | | |
| PGOOD Delay | | | 120 | | | μs |
| PGOOD Pull-Down Resistance | $V_{PGOOD} = 0.1\text{V}$ | | 10 | 20 | | Ω |

### Oscillator and MODE/SYNC

| | | | | | | |
| MODE/SYNC No Clock Detect Time | | | 10 | | | μs |'''
INA_P4 = r'''| | | MIN | MAX | UNIT |
| V <sub>IN+</sub> , V <sub>IN-</sub> | Analog inputs | Differential (V <sub>IN+</sub> ) – (V <sub>IN-</sub> ) <sup>(2)</sup> | –42 | V |
| | | V <sub>IN+</sub> , V <sub>IN-</sub> , with respect to GND <sup>(3)</sup> | 42 | |

### ESD Ratings

| | | VALUE | UNIT |
| V <sub>(ESD)</sub> | Electrostatic discharge | Human-body model (HBM), per ANSI/ESDA/JEDEC JS-001 <sup>(1)</sup> | ±3000 |
| | | Charged-device model (CDM), per JEDEC specification JESD22-C101 <sup>(2)</sup> | ±1000 |'''
INA_P5 = r'''| PARAMETER | | CONDITIONS | MIN | TYP | MAX | UNIT |
| $E_G$ | Gain error | $V_{\text{OUT}} = 0.1\text{ V to } V_S - 0.1\text{ V}$ | A1 devices | -0.04% | ±0.2% | |
| RVRR | Reference voltage rejection ratio | $V_{\text{REF}} = 100\text{ mV to } V_S - 100\text{ mV}$ ,<br>$T_A = -40^\circ\text{C to } +125^\circ\text{C}$ | A1 devices | ±2 | ±10 | µV/V |
| $V_{\text{ZL}}$ | Zero current output voltage | $V_S = 1.8\text{ V}$ , $R_L = 10\text{ k}\Omega$ to GND,<br>$T_A = -40^\circ\text{C to } +125^\circ\text{C}$ , $V_{\text{SENSE}} = 0\text{ mV}$ ,<br>$V_{\text{REF}} = 0\text{ V}$ | A1, A2, A3 devices | $(V_{\text{GND}}) + 1$ | $(V_{\text{GND}}) + 3$ | mV |'''


class GeometryTests(unittest.TestCase):
    def check(self, name, page, snippet):
        with pymupdf.open(v.ROOT / (name + '.pdf')) as document:
            return v.geometry_issues(f'{{{page-1}}}----------------\n' + snippet, document)

    def assert_shift(self, issues, parameter, value, md_column, pdf_column):
        matches = [i for i in issues if parameter in i['parameter'] or parameter in i['row']]
        self.assertTrue(any(i['type'] == 'geometry column mismatch'
                            and i['value'] == value and i['md_column'] == md_column
                            and i['pdf_column'] == pdf_column for i in matches), matches)
        for item in matches:
            self.assertEqual(item['confidence'], 'high')
            self.assertEqual(item['line'], item['md_line'])
            self.assertGreater(item['page'], 0)

    def test_ltc_pmos_merge(self):
        issues, stats = self.check('ltc3315a', 3, LTC_P3)
        for value, md_col, pdf_col in [('2.9', 'TYP', 'MIN'), ('3.2', 'MAX', 'TYP'), ('3.5', 'UNIT', 'MAX')]:
            self.assert_shift(issues, 'PMOS Current Limit', value, md_col, pdf_col)
        self.assertEqual(stats['mismatched'], 1)

    def test_ltc_empty_continuation_headers(self):
        issues, stats = self.check('ltc3315a', 4, LTC_P4)
        for parameter, value, md_col, pdf_col in [
                ('Maximum Duty Cycle', '100', 'TYP', 'MIN'),
                ('PGOOD Delay', '120', 'MIN', 'TYP'),
                ('PGOOD PullDown Resistance', '10', 'MIN', 'TYP'),
                ('PGOOD PullDown Resistance', '20', 'TYP', 'MAX'),
                ('MODE/SYNC No Clock Detect Time', '10', 'MIN', 'TYP')]:
            self.assert_shift(issues, parameter, value, md_col, pdf_col)
        self.assertEqual(stats['mismatched'], 4)
        # A completely headerless block can use the page PDF schema, too.
        issues, _ = self.check('ltc3315a', 4, '| PGOOD Delay | | | 120 | | | μs |')
        self.assert_shift(issues, 'PGOOD Delay', '120', 'MIN', 'TYP')

    def test_ina_absolute_and_esd(self):
        issues, stats = self.check('ina190', 4, INA_P4)
        self.assert_shift(issues, 'Analog inputs', '-42', 'MAX', 'MIN')
        self.assertTrue(any(i['type'] == 'geometry missing value' and i['pdf_column'] == 'MAX'
                            and i['value'] == '42' for i in issues))
        self.assertTrue(any(i['type'] == 'geometry missing value' and i['pdf_column'] == 'MIN'
                            and v.normalize(i['value']) == 'GND -0.3' for i in issues))
        self.assert_shift(issues, 'Humanbody', '+-3000', 'UNIT', 'VALUE')
        self.assert_shift(issues, 'Chargeddevice', '+-1000', 'UNIT', 'VALUE')
        self.assertEqual(stats['mismatched'], 4)

    def test_ina_device_conditions(self):
        issues, stats = self.check('ina190', 5, INA_P5)
        for parameter, value in [('Gain error', 'A1 devices'), ('RVRR', 'A1 devices'),
                                 ('Zero current output voltage', 'A1, A2, A3 devices')]:
            self.assert_shift(issues, parameter, value, 'MIN', 'CONDITIONS')
        self.assertEqual(stats['mismatched'], 3)

    def test_current_correct_rows_verified(self):
        for name, page, parameter in [('ltc3315a', 4, 'NMOS Current Limit'),
                                      ('ina190', 4, 'Supply voltage'), ('ina190', 5, 'CMRR')]:
            with self.subTest(name=name, parameter=parameter):
                text = v.split_pages(v.locate_md(name).read_text())[0][page-1]
                block = next(b for b in v.table_blocks(text) if any(parameter in ' '.join(c) for _, c in b))
                row = next(c for _, c in block if parameter in ' '.join(c))
                header = next(c for _, c in block if any(v.normalize(cell) == 'MIN' for cell in c))
                snippet = '\n'.join('| ' + ' | '.join(c) + ' |' for c in [header, row])
                issues, stats = self.check(name, page, snippet)
                self.assertEqual(issues, [])
                self.assertEqual(stats['verified_ok'], 1, stats)

    def test_value_fallback_catches_tps_missing_max(self):
        # tps6287b20 p10 (pre-fix Datalab rows): TI values shifted into MIN, MAX lost.
        text = ('| PARAMETER | | TEST CONDITIONS | MIN | TYP | MAX | UNIT |\n'
                '| $R_{DS(ON)}$ | High-side FET static on-resistance | $V_{IN} = 3.3\\text{ V}$ | 3.4 | | | m $\\Omega$ |\n'
                '| $t_{off, min}$ | Minimum off-time of HS FET | $V_{IN} = 5\\text{ V}$ | 70 | | | ns |')
        issues, stats = self.check('tps6287b20', 10, text)
        self.assert_shift(issues, 'Highside FET static', '3.4', 'MIN', 'TYP')
        self.assertTrue(any(i['type'] == 'geometry missing value' and i['value'] == '6.4' for i in issues))
        self.assert_shift(issues, 'Minimum offtime', '70', 'MIN', 'TYP')
        self.assertTrue(any(i['type'] == 'geometry missing value' and i['value'] == '100' for i in issues))

    def test_adi_title_case_header_and_right_conditions(self):
        # ADI layout: Parameter | Min | Typ | Max | Unit | Test Conditions/Comments.
        text = v.split_pages(v.locate_md('ad5593r').read_text())[0][3]
        block = next(b for b in v.table_blocks(text) if any(v.normalize(c) == 'Min' or c.strip() == 'Min' for _, cs in b for c in cs))
        snippet = '\n'.join('| ' + ' | '.join(c) + ' |' for _, c in block)
        issues, stats = self.check('ad5593r', 4, snippet)
        self.assertEqual([i for i in issues if i['type'].startswith('geometry')], [])
        self.assertGreater(stats['verified_ok'], 3, stats)

    def test_unit_with_digits_is_not_a_mismatch(self):
        text = ('| Parameter | Min | Typ | Max | Unit | Test Conditions/Comments |\n'
                '| AD5711R | -0.625 | | +0.625 | LSB <sub>12</sub> | |')
        issues, _ = self.check('ad5711r-ad5710r', 4, text)
        self.assertFalse(any('UNIT' in str(i.get('pdf_column')) for i in issues))

    def test_html_and_missing_unit(self):
        snippet = '''<table><tr><th>PARAMETER</th><th>MIN</th><th>TYP</th><th>MAX</th><th>UNIT</th></tr>
<tr><td>PGOOD Delay</td><td>120</td><td></td><td></td><td>V</td></tr></table>'''
        issues, _ = self.check('ltc3315a', 4, snippet)
        self.assert_shift(issues, 'PGOOD Delay', '120', 'MIN', 'TYP')
        self.assertTrue(any(i['value'] == 'V' and i['md_column'] == 'UNIT' for i in issues))


    def test_reviewed_false_positive_samples(self):
        cases = [
            ('lt1965fb', 4, 'Dropout Voltage'),
            ('tps22990', 6, 'ISD, VBIAS'),
            ('tps22990', 7, 'VIN = 2.5 V'),
            ('tps63802', 6, 'VPG,rising'),
            ('ltc2975', 7, 'TUEVS'),
            ('max31730', 2, 'Remote Temperature Accuracy'),
            ('max31730', 3, 'Local Temperature Accuracy'),
        ]
        for name, page, fragment in cases:
            with self.subTest(name=name, fragment=fragment):
                text = v.split_pages(v.locate_md(name).read_text())[0][page-1]
                block = next(b for b in v.table_blocks(text)
                             if any(fragment in v.normalize(' '.join(c)) for _, c in b))
                row = next(c for _, c in block if fragment in v.normalize(' '.join(c)))
                header = next(c for _, c in block if any(v.normalize(cell) == 'MIN' for cell in c))
                snippet = '\n'.join('| ' + ' | '.join(c) + ' |' for c in [header, row])
                issues, _ = self.check(name, page, snippet)
                self.assertEqual(issues, [])


    def test_equal_values_need_separate_occurrences(self):
        doc = pymupdf.open()
        page = doc.new_page()
        for x, word in [(360, 'MIN'), (420, 'TYP'), (480, 'MAX'), (540, 'UNIT')]:
            page.insert_text((x, 100), word)
        page.insert_text((60, 130), 'Supply voltage')
        for x, word in [(360, '6.00'), (480, '+6'), (540, 'V')]:
            page.insert_text((x, 130), word)
        text = '| PARAMETER | MIN | TYP | MAX | UNIT |\n| Supply voltage | 6 | | | V |'
        result = v.geometry_issues(text, doc)
        self.assertEqual(result, v.geometry_issues(text, doc))
        issues, stats = result
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['type'], 'geometry missing value')
        self.assertEqual(issues[0]['pdf_column'], 'MAX')
        self.assertEqual(stats['mismatched'], 1)
        doc.close()

    def test_numeric_range_condition_selects_sub_row(self):
        # sn74avc4t774 p7: parameter label is centred on the 3rd sub-row;
        # the "1.1V to 1.3V" condition must pick the first one.
        doc = pymupdf.open()
        p = doc.new_page()
        for x, word in [(330, 'VCCO'), (430, 'MIN'), (495, 'MAX'), (526, 'UNIT')]:
            p.insert_text((x, 100), word)
        rows = [(130, '1.1V to 1.3V', '-3'), (150, '1.4V to 1.6V', '-6'), (170, '1.65V to 1.95V', '-8')]
        for y, cond, val in rows:
            p.insert_text((315, y), cond)
            p.insert_text((500, y), val)
        p.insert_text((60, 170), 'High-level output current')
        p.insert_text((526, 170), 'mA')
        text = ('| PARAMETER | VCCO | MIN | MAX | UNIT |\n'
                '| High-level output current | 1.1V to 1.3V | | -3 | mA |\n'
                '| | 1.4V to 1.6V | | -6 | |\n'
                '| | 1.65V to 1.95V | | -8 | |')
        issues, stats = v.geometry_issues(text, doc)
        self.assertEqual([i for i in issues if i['type'].startswith('geometry')], [])
        doc.close()

    def test_value_fallback_abstains_when_values_recur_in_other_table(self):
        # tps22990 p6: a bare "-40C to +105C ... 6" row exists six times in one
        # table; a single "6" row in another table must not be picked.
        doc = pymupdf.open()
        p = doc.new_page()
        for top in (100, 400):
            for x, word in [(420, 'TA'), (468, 'MIN'), (492, 'TYP'), (515, 'MAX'), (537, 'UNIT')]:
                p.insert_text((x, top), word)
        for y in (130, 170, 210):
            p.insert_text((395, y), '-40C to +105C')
            p.insert_text((526, y), '6')
        p.insert_text((395, 430), '-40C to +105C')
        p.insert_text((522, 430), '59')
        p.insert_text((395, 440), '-40C to +85C')
        p.insert_text((496, 440), '4.5')
        p.insert_text((526, 440), '6')
        text = '| PARAMETER | TA | MIN | TYP | MAX | UNIT |\n| | -40C to +105C | | | 6 | |'
        issues, stats = v.geometry_issues(text, doc)
        self.assertEqual(issues, [])
        doc.close()

    def test_ambiguous_rows_and_unrelated_tables_abstain(self):
        doc = pymupdf.open()
        p = doc.new_page()
        for x, word in [(360, 'MIN'), (420, 'TYP'), (480, 'MAX'), (540, 'UNIT')]:
            p.insert_text((x, 100), word)
        for y in (130, 160):
            p.insert_text((60, y), 'Supply voltage')
            p.insert_text((480, y), '6')
        issues, stats = v.geometry_issues('| PARAMETER | MIN | TYP | MAX | UNIT |\n| Supply voltage | 6 | | | V |', doc)
        self.assertEqual(issues, [])
        self.assertEqual(stats['unverifiable'], 1)
        doc.close()
        # The real thermal table follows MIN/NOM/MAX on the same page.
        issues, stats = self.check('ina190', 4, '| THERMAL METRIC | | DCK | DDF | RSW | UNIT |\n'
                                   '| RthetaJA | Junction-to-ambient thermal resistance | 137.2 | 170.7 | 163.8 | °C/W |')
        self.assertEqual(issues, [])
        # no MIN/TYP/MAX/VALUE columns: abstain, reported as out of scope
        self.assertEqual(stats['unverifiable'] + stats['out_of_scope'], 1)


if __name__ == '__main__':
    unittest.main()
