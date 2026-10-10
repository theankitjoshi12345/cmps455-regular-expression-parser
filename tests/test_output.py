"""Golden-output checks for the assignment expressions."""

import unittest

from regex_parser.recognizer import RegexRecognizer
from regex_parser.scanner import tokenize


class OutputTests(unittest.TestCase):
    def render(self, expression: str) -> str:
        return RegexRecognizer.render(
            RegexRecognizer(tokenize(expression)).parse()
        )

    def test_two_golden_tree(self) -> None:
        self.assertEqual(
            self.render("two"),
            "\n".join(
                (
                    "RE",
                    "    S_RE",
                    "        B_RE",
                    "            E_RE",
                    "                t CHAR",
                    "        B_RE",
                    "            E_RE",
                    "                w CHAR",
                    "        B_RE",
                    "            E_RE",
                    "                o CHAR",
                )
            ),
        )

    def test_all_assignment_examples_have_required_root_and_token_output(self):
        examples = ("two", "t|w|o", "[two]", "[^two]", "t(oo?|wo)",
                    r"(\<(/?[^\\>]+)\>)")
        for expression in examples:
            with self.subTest(expression=expression):
                output = self.render(expression)
                self.assertTrue(output.startswith("RE\n"))
                self.assertIn("S_RE", output)
                self.assertIn("B_RE", output)
                self.assertIn("E_RE", output)

    def test_invalid_token_reports_location(self) -> None:
        with self.assertRaisesRegex(
            ValueError, r"unexpected trailing token ERROR at line 1, column 1"
        ):
            RegexRecognizer(tokenize("a\0")).parse()


if __name__ == "__main__":
    unittest.main()
