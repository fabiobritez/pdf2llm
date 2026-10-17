"""Focused conversion cases and independent fidelity regression tests."""
import unittest
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
        self.assertEqual(inline(r'V_{IN+} \pm 12'), 'V_IN+ ± 12')
        self.assertEqual(inline(r' A   B\_C  '), 'A B_C')

    def test_tables(self):
        source = '| A | | MIN | | MAX |\n|---|---|---|---|---|\n| x | | 1 | | 2 |\n| y | | | ● | 3 |\n'
        out = compact(source)
        self.assertIn('|A|MIN||MAX|\n|-|-|-|-|\n|x|1||2|\n|y||●|3|', out)
        self.assertFalse(check(source, out)['failures'])
        self.assertEqual(out.count('●'), source.count('●') + 1)  # legend

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
