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


if __name__ == '__main__':
    unittest.main()
