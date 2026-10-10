"""Tests for the Issue 4 elementary regular-expression rule."""

import unittest

from regex_parser.recognizer import RecognitionError, RegexRecognizer
from regex_parser.scanner import TokenType, tokenize


class ElementaryRegularExpressionTests(unittest.TestCase):
    def parse(self, expression: str):
        return RegexRecognizer(tokenize(expression)).elementary_re()

    def test_character_and_period_alternatives(self) -> None:
        self.assertEqual(self.parse("a").children[0].name, "CHAR_OR_META")
        self.assertEqual(self.parse(".").children[0].name, "PERIOD")

    def test_positive_and_negative_set_alternatives(self) -> None:
        positive = self.parse("[abc]")
        negative = self.parse("[^abc]")
        self.assertEqual(positive.children[0].name, TokenType.LPOSSET)
        self.assertEqual(negative.children[0].name, TokenType.LNEGSET)
        self.assertEqual(
            positive.children[0].token.typ, TokenType.LPOSSET
        )
        self.assertEqual(
            negative.children[0].token.typ, TokenType.LNEGSET
        )

    def test_parenthesized_expression(self) -> None:
        node = self.parse("(a)")
        self.assertEqual(
            [child.name for child in node.children],
            ["LPAREN", "RE", "RPAREN"],
        )

    def test_nested_parenthesized_expression(self) -> None:
        node = self.parse("((a))")
        self.assertEqual(node.children[1].children[0].name, "S_RE")

    def test_malformed_delimiters_are_rejected(self) -> None:
        for expression in ("()", "(a", "[abc", "[]", "[^]"):
            with self.subTest(expression=expression):
                with self.assertRaises(RecognitionError):
                    self.parse(expression)


if __name__ == "__main__":
    unittest.main()
