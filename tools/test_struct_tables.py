import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_struct_tables as c  # noqa: E402


def words(*items):
    # (page, y, x, text) as produced by page_words
    return [(1, y, x, c.squash(t)) for y, x, t in items]


class StructTableTests(unittest.TestCase):
    def test_row_on_one_line_in_order(self):
        w = words((100, 10, "3"), (100, 50, "VDD"), (100, 90, "Power"), (120, 10, "4"), (120, 50, "GND"))
        self.assertEqual(c.check_row([c.tokens("3"), c.tokens("V<sub>DD</sub>")], w)[0], "ok")

    def test_pin_number_paired_with_other_name(self):
        w = words((100, 10, "3"), (100, 50, "VDD"), (120, 10, "4"), (120, 50, "GND"))
        self.assertEqual(c.check_row([c.tokens("4"), c.tokens("VDD")], w)[0], "unpaired")

    def test_misspelt_name_is_missing(self):
        w = words((100, 10, "A1"), (100, 50, "VSENSEM1"))
        status, detail = c.check_row([c.tokens("A1"), c.tokens("$V_{SENEM1}$")], w)
        self.assertEqual((status, detail), ("missing", ["senem1"]))

    def test_vertically_centred_cell_is_loose(self):
        w = words((100, 10, "b[2:0]"), (95, 60, "Iout_oc_delay,"), (105, 60, "Iout_uc_delay"))
        self.assertEqual(c.check_row([c.tokens("b[2:0]"), c.tokens("Iout_oc_delay")], w)[0], "loose")

    def test_latex_and_overline_are_plain(self):
        self.assertEqual(c.tokens(r"$\overline{\text{EN}}$"), ["en"])
        self.assertEqual(c.tokens("m$\\Omega$"), ["mω"])

    def test_structural_headers(self):
        self.assertTrue(c.structural(["Bits", "Bit Name", "Description", "Reset", "Access"]))
        self.assertTrue(c.structural(["PIN", "", "TYPE (1)", "DESCRIPTION"]))
        self.assertFalse(c.structural(["PARAMETER", "MIN", "TYP", "MAX", "UNIT"]))

    def test_prose_pin_entry(self):
        m = c.PROSE.match("**EN1 (Pin 1/Ball B3):** Enable Input")
        self.assertEqual(c.tokens(m[1]), ["en1", "pin", "1", "ball", "b3"])
        self.assertTrue(c.in_order(["en1", "pin", "1"], "en1pin1ballb3enableinput"))

    def test_bit_layout_shift_is_flagged(self):
        class Page:
            def get_text(self, kind):
                ws = [(x - 3, 155, x + 3, 161, str(7 - k)) for k, x in enumerate(range(86, 586, 62))]
                return ws + [(370, 169, 390, 175, "DROOPEN"), (440, 169, 460, 175, "SINGLE"),
                            (190, 169, 220, 175, "RESERVED")]
        header = ["7", "6", "5", "4", "3", "2", "1", "0"]
        shifted = [(10, ["RESERVED", "", "", "", "DROOPEN", "SINGLE", "", ""])]
        right = [(10, ["RESERVED", "", "", "", "", "DROOPEN", "SINGLE", ""])]
        self.assertEqual([i["tokens"] for i in c.bit_columns([Page()], 1, header, shifted)], [["DROOPEN"]])
        self.assertEqual(c.bit_columns([Page()], 1, header, right), [])


if __name__ == "__main__":
    unittest.main()
