"""Focused recognizer tests for the assignment grammar."""

import contextlib
import io
import unittest

from regex_parser.recognizer import RecognitionError, RegexRecognizer
from regex_parser.scanner import tokenize


EXAMPLES = (
    "two",
    "t|w|o",
    "[two]",
    "[^two]",
    "t(oo?|wo)",
    r"(\<(/?[^\>]+)\>)",
)


def parse_output(expression: str) -> str:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        RegexRecognizer(tokenize(expression)).parse()
    return output.getvalue().rstrip()


class RecognizerTests(unittest.TestCase):
    def test_all_assignment_examples_are_valid(self) -> None:
        for expression in EXAMPLES:
            with self.subTest(expression=expression):
                RegexRecognizer(tokenize(expression)).parse()

    def test_two_has_required_tree_and_indentation(self) -> None:
        self.assertEqual(
            parse_output("two"),
            "\n".join(
                (
                    "RE",
                    "    S_RE",
                    "        B_RE",
                    "            E_RE",
                    "                CHAR_OR_META",
                    "                    t CHAR",
                    "        B_RE",
                    "            E_RE",
                    "                CHAR_OR_META",
                    "                    w CHAR",
                    "        B_RE",
                    "            E_RE",
                    "                CHAR_OR_META",
                    "                    o CHAR",
                )
            ),
        )

    def test_sets_and_escaped_metacharacters_are_printed(self) -> None:
        output = parse_output(r"[^a\]]")
        self.assertIn("[^ LNEGSET", output)
        self.assertIn("SITEMS", output)
        self.assertIn(r"\ BSLASH", output)
        self.assertIn("] RSET", output)

    def test_invalid_expressions_are_rejected(self) -> None:
        for expression in ("", "|a", "a|", "a||b", "(a", "a)", "[]", r"\q", "a**"):
            with self.subTest(expression=expression):
                with self.assertRaises(RecognitionError):
                    RegexRecognizer(tokenize(expression)).parse()


if __name__ == "__main__":
    unittest.main()
