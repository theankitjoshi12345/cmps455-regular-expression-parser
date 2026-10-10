"""Tests for the Issue 5 basic regular-expression rule."""

import unittest

from regex_parser.recognizer import RecognitionError, RegexRecognizer
from regex_parser.scanner import TokenType, tokenize


class BasicRegularExpressionTests(unittest.TestCase):
    def parse(self, expression: str):
        return RegexRecognizer(tokenize(expression)).basic_re()

    def test_accepts_an_elementary_expression_without_quantifier(self) -> None:
        node = self.parse("a")
        self.assertEqual(node.name, "B_RE")
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].name, "E_RE")

    def test_accepts_each_optional_quantifier(self) -> None:
        for operator, token_type in (
            ("*", TokenType.STAR),
            ("+", TokenType.PLUS),
            ("?", TokenType.QMARK),
        ):
            with self.subTest(operator=operator):
                node = self.parse("a" + operator)
                self.assertEqual(node.name, "B_RE")
                self.assertEqual(len(node.children), 2)
                self.assertEqual(node.children[1].name, token_type)
                self.assertEqual(node.children[1].token.typ, token_type)

    def test_quantifier_is_not_detached_or_repeated(self) -> None:
        for expression in ("*", "+", "?", "a**", "a+?", "a??"):
            with self.subTest(expression=expression):
                with self.assertRaises(RecognitionError):
                    self.parse(expression)


if __name__ == "__main__":
    unittest.main()
