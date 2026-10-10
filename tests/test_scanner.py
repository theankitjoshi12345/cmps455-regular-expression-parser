"""Tests for the regular-expression scanner."""

import unittest

from regex_parser.scanner import TokenStream, TokenType, tokenize


class ScannerTests(unittest.TestCase):
    def test_metacharacters_and_ordinary_characters(self) -> None:
        tokens = list(tokenize("a|b*+?.()"))
        self.assertEqual(
            [token.typ for token in tokens],
            [
                TokenType.CHAR,
                TokenType.VERT,
                TokenType.CHAR,
                TokenType.STAR,
                TokenType.PLUS,
                TokenType.QMARK,
                TokenType.PERIOD,
                TokenType.LPAREN,
                TokenType.RPAREN,
            ],
        )
        self.assertEqual([token.value for token in tokens], list("a|b*+?.()"))

    def test_sets_escapes_and_angle_brackets(self) -> None:
        tokens = list(tokenize(r"[^a-z]\<x\>"))
        self.assertEqual(
            [token.typ for token in tokens],
            [
                TokenType.NSET,
                TokenType.CHAR,
                TokenType.CHAR,
                TokenType.CHAR,
                TokenType.RSET,
                TokenType.BACKSLASH,
                TokenType.LANGLE,
                TokenType.CHAR,
                TokenType.BACKSLASH,
                TokenType.RANGLE,
            ],
        )

    def test_locations_and_end_of_line(self) -> None:
        tokens = list(tokenize("ab\nc"))
        self.assertEqual(
            [(token.value, token.line, token.column) for token in tokens],
            [("a", 1, 0), ("b", 1, 1), ("\n", 1, 2), ("c", 2, 0)],
        )

    def test_stream_peek_and_advance(self) -> None:
        stream = TokenStream(tokenize("ab"))
        self.assertEqual(stream.peek().value, "a")
        self.assertEqual(stream.peek(1).value, "b")
        self.assertEqual(stream.advance().value, "a")
        self.assertEqual(stream.advance().value, "b")
        self.assertIsNone(stream.peek())
        self.assertIsNone(stream.advance())

    def test_invalid_control_character_is_error(self) -> None:
        token = next(tokenize("a\0"))
        self.assertEqual(token.typ, TokenType.CHAR)
        self.assertEqual(next(tokenize("\0")).typ, TokenType.ERROR)


if __name__ == "__main__":
    unittest.main()
