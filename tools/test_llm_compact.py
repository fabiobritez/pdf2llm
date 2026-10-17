"""Focused conversion cases and independent fidelity regression tests."""
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from tools import check_llm_fidelity as fidelity
from tools.llm_compact import compact, inline, latex, sources
from tools.check_llm_fidelity import check, tokens


class CompactTests(unittest.TestCase):
    def test_latex_subscripts(self):
        self.assertEqual(inline(r'$V_{OS}$ and $V_{IN+}$ and $V_{A_{B}}$'), 'V_OS and V_IN+ and V_A_B')
        self.assertEqual(inline(r'$-40^{\circ}\text{C}$ $10^{3}$ $\mu\Omega$'), '-40°C 10^3 µΩ')

    def test_latex_symbols(self):
        self.assertEqual(latex(r'\pm\leq\geq\neq\times\cdot\approx\cong\equiv\sim\infty\Delta'), '±≤≥≠×·≈≅≡~∞Δ')
        self.assertEqual(latex(r'\alpha\beta\theta\Psi\pi\Sigma\Phi'), 'αβθΨπΣΦ')
        self.assertEqual(latex(r'\text{hi}\mathrm{R}\mathbf{B}\textbf{T}\unknown{7}'), 'hiRBTunknown7')
        self.assertEqual(latex(r'\frac{a}{b} \frac{a + 2}{b - 3} \sqrt{x} \overline{X}'), 'a/b (a + 2)/(b - 3) √(x) /X')
        self.assertEqual(latex(r'\left(x\right) \% \_ \# \&'), '(x) % _ # &')

    def test_html(self):
        self.assertEqual(inline('X <sub>OS</sub> <sup>(1)</sup> <sup>x</sup>'), 'X_OS (1) ^x')
        self.assertEqual(inline('<b>a</b> <i>b</i> <u>c</u> <a href="#">t</a> [u](#) &amp; &#177;'), 'a b c t u & ±')
        self.assertEqual(inline('a<br>b<br/>c', table=True), 'a; b; c')
        self.assertEqual(inline('a<br>b'), 'a\nb')
        self.assertEqual(inline('V <sub>SENSEP<sub>n</sub></sub>'), 'V_SENSEP_n')
        self.assertEqual(inline('a `b   c` d'), 'a `b   c` d')
        self.assertEqual(inline(r'V_{IN+} \pm 12'), 'V_IN+ ±12')
        self.assertEqual(inline(r' A   B\_C  '), 'A B_C')

    def test_tables(self):
        source = '| A | | MIN | | MAX |\n|---|---|---|---|---|\n| x | | 1 | | 2 |\n| y | | | ● | 3 |\n'
        out = compact(source)
        self.assertIn('|A|MIN||MAX|\n|-|-|-|-|\n|x|1||2|\n|y||●|3|', out)
        self.assertFalse(check(source, out)['failures'])
        self.assertEqual(out.count('●'), source.count('●') + 1)  # legend

    def test_nested_lists(self):
        source = ('- Low power:\n    - Supply\n        * Detail\n    - Current\n'
                  '- Accuracy:\n  - Offset\n\n  - Gain\n\n## Next\n'
                  '1. Parent\n    1. Child\n        1. Grandchild\n2. Sibling')
        expected = ('- Low power:\n  - Supply\n    * Detail\n  - Current\n'
                    '- Accuracy:\n  - Offset\n\n  - Gain\n\n## Next\n'
                    '1. Parent\n  1. Child\n    1. Grandchild\n2. Sibling')
        self.assertIn(expected, compact(source))
        self.assertIn('- Parent\n  - Child', compact('- Parent\n\t- Child'))

    def test_spacing_cleanup(self):
        cases = {
            r'50 $\mu$ A': '50 µA',
            r'$\pm$ 15 $\mu$ V': '±15 µV',
            '± 0.2%': '±0.2%', 'V_S :': 'V_S:',
            '+125°C ,': '+125°C,', '( /OE )': '(/OE)',
            'Δ T_I': 'ΔT_I', 'μ A': 'μA',
            'x ,<br> y': 'x; y',
            '( a ) [ b ] x ; y : z . Next': '(a) [b] x; y: z. Next',
            '1 2 3 . 4': '1 2 3. 4',
            '1 .2': '1 .2',
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(inline(source, table=True), expected)
                self.assertIn('|' + expected + '|', compact('|Text|\n|-|\n|' + source + '|'))

    def test_numeric_minus(self):
        source = '–40 −12 x =−2 (–3) y –4 word–word word – word 1–2'
        expected = '-40 -12 x =-2 (-3) y -4 word–word word – word 1–2'
        self.assertEqual(inline(source), expected)
        self.assertIn('|-40|-12|', compact('|MIN|MAX|\n|-|-|\n|–40|−12|'))

    def test_emphasis(self):
        source = '**bold** *italic* _italic_ __bold__ ***both*** **V_OS** V_OS A_B_C 2 * 3'
        expected = 'bold italic italic bold both V_OS V_OS A_B_C 2 * 3'
        self.assertEqual(inline(source), expected)
        self.assertIn('### Title V_OS', compact('### **Title** _V_OS_'))
        self.assertIn('|bold|V_OS|', compact('|**bold**|*V_OS*|'))
        self.assertIn('* Item', compact('* **Item**'))
        self.assertIn('Package\n\nTop View', compact('**Package\n\nTop View**'))
        self.assertIn('- Top View: Shows', compact('- Top View:** Shows'))

    def test_cleanup_preserves_code(self):
        literal = '**bold** _em_ V_OS ± 15 µ A Δ T_I ( /OE ) –12 1 2'
        for fence in ('```', '~~~'):
            self.assertIn(fence + '\n' + literal + '\n' + fence,
                          compact(fence + '\n' + literal + '\n' + fence))
        for delimiter in ('`', '``'):
            span = delimiter + literal + delimiter
            self.assertEqual(inline('**Prose** ' + span + ' , ± 2'), 'Prose ' + span + ', ±2')
        self.assertEqual(inline('``a ` b``'), '``a ` b``')

    def test_escaped_table_pipes(self):
        src = r'|Parameter|MIN|MAX|' + '\n|-|-|-|\n' + r'|Voltage \|V\||1|2|'
        out = compact(src)
        self.assertIn(r'Voltage \|V\|', out)
        self.assertNotIn(r'\\|', out)
        self.assertFalse(check(src, out)['failures'])

    def test_header_only_column_not_dropped(self):
        self.assertIn('|A|MIN|Header|', compact('|A|MIN|Header|\n|-|-|-|\n|x|1||'))

    def test_figures(self):
        out = compact('![A 1 V graph](a.jpg)\n\nA 1 V graph\n\n**Figure 7. Caption**')
        self.assertEqual(out.count('A 1 V graph'), 1)
        self.assertIn('Figure (description only, not data): A 1 V graph', out)
        self.assertIn('\nFigure 7. Caption', out)
        self.assertIn('graph 2 V extended', compact('![graph](a.jpg)\n\ngraph 2 V extended'))
        self.assertIn('different 3 V', compact('![graph](a.jpg)\n\ndifferent 3 V'))
        self.assertEqual(compact('![MUX_OUT](a.jpg)\n\nMUX\\_OUT').count('MUX_OUT'), 1)

    def test_sections_and_icons(self):
        src = ('![Tools & Software icon](a.jpg)\n\nTools & Software icon\n\n'
               '## Table of Contents\n\n|Title.....|2|\n\n### Subsection\nignored 4\n'
               '## Revision History\nold 123\n### Revision A\n456\n## Specifications\nkeep 789')
        out = compact(src)
        for removed in ['Tools & Software', 'Title', 'ignored', '123', '456']:
            self.assertNotIn(removed, out)
        self.assertIn('## Revision History\n(Revision history omitted; see PDF.)', out)
        self.assertIn('keep 789', out)
        out = compact('|Feature.....|1|\n|-|-|\n|Application.....|2|\n\nkeep 8')
        self.assertNotIn('Feature', out)
        self.assertIn('keep 8', out)

    def test_misleveled_sections(self):
        source = '# TABLE OF CONTENTS\n|Foo.....|2|\n\n{2}-----\n## Specifications\nkeep 9'
        self.assertIn('keep 9', compact(source))
        source = '## Revision History\n## 8/2023—Rev. G to H\nold 1\n## Specifications\nkeep 9'
        self.assertNotIn('old 1', compact(source))
        self.assertIn('keep 9', compact(source))

    def test_pages_and_idempotence(self):
        out = compact('{0}-----\n\nA   $V_{OS}$\n\n\n{11}-----\n● 12')
        self.assertIn('[p1]', out)
        self.assertIn('[p12]', out)
        self.assertNotIn('\n\n\n', out)
        self.assertEqual(out, compact(out))

    def test_code(self):
        self.assertIn('a   $V_{IN}$', compact('```\na   $V_{IN}$\n```'))

    def test_checker_catches_loss(self):
        src = '|Parameter|MIN|MAX|\n|-|-|-|\n|Voltage|1|12|\n|Current|2|2|'
        good = compact(src)
        self.assertFalse(check(src, good)['failures'])
        self.assertTrue(check(src, good.replace('|Voltage|1|12|', '|Voltage|1||'))['failures'])
        self.assertTrue(check(src, good.replace('|Current|2|2|', '|Current|2||'))['failures'])
        self.assertTrue(check(src, good.replace('|Voltage|1|12|', '|Voltage|12|1|'))['failures'])
        self.assertTrue(check(src, good.replace('|Current|2|2|', ''))['failures'])
        self.assertTrue(check(src, good.replace('Voltage', ''))['failures'])
        self.assertTrue(check(src, good.replace('|Parameter|MIN|MAX|', '|Parameter|LOW|HIGH|'))['failures'])

    def test_checker_signs_bullets_and_multiplicity(self):
        self.assertEqual(tokens('−12 –12 -12 ±2 +3')[0], {'-12': 3, '±2': 1, '+3': 1})
        src = '|Parameter|MIN|TYP|\n|-|-|-|\n|Voltage ●|±12|12|'
        good = compact(src)
        for bad in [good.replace('±12', '12'), good.replace('Voltage ●', 'Voltage'), good.replace('|±12|12|', '|±12||')]:
            self.assertTrue(check(src, bad)['failures'])

    def test_checker_cli_rejects_prose_numeric_loss(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            sheet = root / 'output' / 'sample'
            sheet.mkdir(parents=True)
            source = '|Parameter|MIN|\n|-|-|\n|Voltage|1|\n\nProse 987'
            (sheet / 'sample.md').write_text(source)
            target = compact(source).replace('Prose 987', 'Prose')
            self.assertFalse(check(source, target)['failures'])
            (sheet / 'sample.llm.md').write_text(target)
            with patch.object(fidelity, 'ROOT', root), patch('sys.argv', ['check_llm_fidelity']), redirect_stdout(StringIO()):
                self.assertEqual(fidelity.main(), 1)
            report = (root / 'reports' / 'llm' / 'fidelity.md').read_text()
            self.assertIn('FAIL: 1 datasheets checked; spec-table failures: 0;', report)
            self.assertEqual(report.count('Before figure deduplication (diagnostic only):'), 1)
            self.assertEqual(report.count('Missing `987`'), 1)

    def test_vendor_legal_spans_and_boundaries(self):
        source = ('### **IMPORTANT NOTICE AND DISCLAIMER**\n\n'
                  'TI PROVIDES TECHNICAL AND RELIABILITY DATA (INCLUDING DATASHEETS).\n\n'
                  'These resources are intended for skilled developers designing with TI products. '
                  'You are responsible for (1) selection and (2) testing.\n\n'
                  "TI's products are provided subject to [TI's Terms of Sale](#).\n\n"
                  'TI objects to and rejects any additional or different terms you may propose.\n\n'
                  'Mailing Address: Texas Instruments, Dallas, Texas 75265\n\n'
                  'Copyright © 2026, Texas Instruments Incorporated\n\nLast updated 10/2025\n\n'
                  '{98}-----\n# PACKAGE OUTLINE\n|Dimension|MIN|MAX|\n|-|-|-|\n|Width|1.25|2.5|\n'
                  '# Orderable Information\nPART123ABC, 3000 per reel\n')
        out = compact(source)
        marker = '(IMPORTANT NOTICE AND DISCLAIMER omitted: vendor boilerplate; see PDF.)'
        self.assertEqual(out.count(marker), 1)
        self.assertIn('### IMPORTANT NOTICE AND DISCLAIMER\n' + marker, out)
        self.assertIn('[p99]', out)
        self.assertNotIn('75265', out)
        self.assertNotIn('2026', out)
        self.assertIn('PART123ABC, 3000 per reel', out)
        self.assertIn('|Width|1.25|2.5|', out)
        self.assertFalse(check(source, out)['failures'])
        self.assertTrue(check(source, out)['deduplicated_numeric']['subset'])
        bad = check(source, out.replace('PART123ABC, 3000', 'PARTABC, '))
        self.assertFalse(bad['deduplicated_numeric']['subset'])

    def test_vendor_support_standard_and_document_lists(self):
        source = ('## Documentation Support\n### Related Documentation\n'
                  '- [SLVA123 application report](#)\n'
                  '### 8.2 Receiving Notification of Documentation Updates\n'
                  'To receive notification of documentation updates, navigate to the device product folder on [ti.com](#). '
                  'Click on *Notifications* to register and receive a weekly digest of any product information that has changed. '
                  'For change details, review the revision history included in any revised document.\n'
                  '{4}-----\n### 8.3 Trademarks\n'
                  'I2C™ is a trademark of NXP Semiconductors.\n'
                  'All other trademarks are the property of their respective owners.\n'
                  '### 8.4 Glossary\n#### [TI Glossary](#)\n\n'
                  'This glossary lists and explains terms, acronyms, and definitions.\n'
                  '## Land Pattern\nPad pitch 0.5 mm\n')
        out = compact(source)
        self.assertEqual(out.count('omitted: vendor boilerplate'), 3)
        self.assertIn('SLVA123 application report', out)
        self.assertIn('Documentation Support', out)
        self.assertIn('Related Documentation', out)
        self.assertIn('[p5]', out)
        self.assertIn('Pad pitch 0.5 mm', out)
        self.assertNotIn('I2C', out)
        self.assertTrue(check(source, out)['deduplicated_numeric']['subset'])

    def test_custom_support_sections_are_retained(self):
        for title in ('Receiving Notification of Documentation Updates', 'Support Resources',
                      'Trademarks', 'Electrostatic Discharge Caution', 'Glossary', 'Community Resources'):
            with self.subTest(title=title):
                source = ('### 7.2 ' + title + '\n\n'
                          'All other trademarks are the property of their respective owners.\n\n'
                          'Device-specific threshold 987 mV.\n#### Custom Details\nPin 456.\n')
                out = compact(source)
                self.assertNotIn('omitted: vendor boilerplate', out)
                self.assertIn('All other trademarks', out)
                self.assertIn('Device-specific threshold 987 mV.', out)
                self.assertFalse(check(source, out.replace('987', ''))['deduplicated_numeric']['subset'])

    def test_vendor_paragraphs_without_headings(self):
        for paragraph in (
                'Information furnished by Analog Devices is believed to be accurate and reliable. No license is granted.',
                'Information furnished by Linear Technology is believed to be accurate and reliable.',
                'Maxim Integrated cannot assume responsibility for use of any circuitry other than its products.',
                'All registered trademarks and trademarks are the property of their respective owners. '
                'Protected by U.S. patents, including 7382303, 7420359 and 8648623.',
                'LT, LTC and Linear Technology are registered trademarks and ThinSOT is a trademark of '
                'Linear Technology Corporation. All other trademarks are the property of their respective owners.'):
            with self.subTest(paragraph=paragraph):
                source = 'Part ABC123\n\n' + paragraph + '\n\n## Mechanical\nHeight 1.2 mm'
                out = compact(source)
                self.assertNotIn(paragraph, out)
                self.assertEqual(out.count('omitted: vendor boilerplate'), 1)
                self.assertIn('Part ABC123', out)
                self.assertIn('Height 1.2 mm', out)
                self.assertTrue(check(source, out)['deduplicated_numeric']['subset'])
                self.assertFalse(check(source, out.replace('1.2', ''))['deduplicated_numeric']['subset'])

    def test_ti_copyright_furniture(self):
        source = ('Copyright © 2016, Texas Instruments Incorporated\n\n'
                  'Value 654\n\nCopyright © 2021 Texas Instruments Incorporated **Submit Document Feedback** 9\n\n'
                  'Copyright © 2016, Texas Instruments Incorporated\n\n'
                  'Copyright © 2025 Other Vendor\n')
        out = compact(source)
        self.assertNotIn('Texas Instruments Incorporated', out)
        self.assertNotIn('omitted:', out)
        self.assertIn('Copyright © 2025 Other Vendor', out)
        self.assertTrue(check(source, out)['deduplicated_numeric']['subset'])
        self.assertFalse(check(source, out.replace('654', ''))['deduplicated_numeric']['subset'])
        self.assertEqual([n for n, _ in fidelity.source_lines(source) if n in (1, 5, 7)], [])

    def test_vendor_patterns_preserve_literals_and_tables(self):
        legal = 'Information furnished by Analog Devices is believed to be accurate and reliable.'
        source = ('```\n' + legal + '\nCopyright © 2026, Texas Instruments Incorporated\n```\n'
                  '## Electrostatic Discharge (ESD) Ratings\n|Parameter|MIN|MAX|\n|-|-|-|\n'
                  '|ESD|1000|2000|\n\n' + legal + '|Model|Package|\n|-|-|\n|ABC123|QFN16|')
        out = compact(source)
        self.assertIn('```\n' + legal + '\nCopyright © 2026, Texas Instruments Incorporated\n```', out)
        self.assertIn('|ESD|1000|2000|', out)
        self.assertIn(legal + '|Model|Package|', out)
        self.assertTrue(check(source, out)['deduplicated_numeric']['subset'])

    def test_all_datasheets(self):
        for path in sources():
            with self.subTest(datasheet=path.parent.name):
                src = path.read_text()
                out = compact(src, str(path.relative_to(path.parents[2])))
                self.assertEqual(out, compact(out))
                result = check(src, out)
                self.assertFalse(result['failures'], result['failures'][:2])
                self.assertTrue(result['deduplicated_numeric']['subset'])


if __name__ == '__main__':
    unittest.main()
