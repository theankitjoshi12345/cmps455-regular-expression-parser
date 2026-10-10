"""Tests for concatenation, alternation, and complete validation."""

import unittest

from regex_parser.recognizer import RecognitionError, RegexRecognizer
from regex_parser.scanner import TokenType, tokenize


class ExpressionGrammarTests(unittest.TestCase):
    def parse(self, expression: str):
        return RegexRecognizer(tokenize(expression)).parse()

    def test_simple_re_parses_concatenation(self) -> None:
        node = self.parse("abc")
        simple = node.children[0]
        self.assertEqual(simple.name, "S_RE")
        self.assertEqual(len(simple.children), 3)
        self.assertTrue(all(child.name == "B_RE" for child in simple.children))

    def test_regular_expression_parses_arbitrary_alternation(self) -> None:
        node = self.parse("a|b|c")
        self.assertEqual(node.name, "RE")
        self.assertEqual(
            [child.name for child in node.children],
            ["S_RE", TokenType.VERT, "S_RE", TokenType.VERT, "S_RE"],
        )

    def test_parentheses_can_contain_alternation_and_concatenation(self) -> None:
        node = self.parse("t(oo?|wo)")
        self.assertEqual(node.children[0].name, "S_RE")

    def test_assignment_examples_parse(self) -> None:
        for expression in ("two", "t|w|o", "[two]", "[^two]", "t(oo?|wo)"):
            with self.subTest(expression=expression):
                self.assertTrue(RegexRecognizer(tokenize(expression)).recognize())

    def test_invalid_boundaries_are_rejected(self) -> None:
        for expression in ("", "|a", "a|", "a||b", "(a", "a)", "[a", "[]"):
            with self.subTest(expression=expression):
                recognizer = RegexRecognizer(tokenize(expression))
                self.assertFalse(recognizer.recognize())
                with self.assertRaises(RecognitionError):
                    RegexRecognizer(tokenize(expression)).parse()


if __name__ == "__main__":
    unittest.main()
