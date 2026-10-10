"""Tests for the Issue 3 recognizer rules."""

import unittest

from regex_parser.recognizer import RecognitionError, RegexRecognizer
from regex_parser.scanner import TokenType, tokenize


class RecognizerTests(unittest.TestCase):
    def test_char_or_meta_accepts_character(self) -> None:
        node = RegexRecognizer(tokenize("a")).char_or_meta()
        self.assertEqual(node.name, "CHAR_OR_META")
        self.assertEqual(node.token.typ, TokenType.CHAR)

    def test_char_or_meta_requires_escape_for_metacharacters(self) -> None:
        node = RegexRecognizer(tokenize(r"\|")).char_or_meta()
        self.assertEqual([child.name for child in node.children], ["BSLASH", "META"])
        with self.assertRaises(RecognitionError):
            RegexRecognizer(tokenize("|")).char_or_meta()

    def test_set_items_accepts_one_or_more_items(self) -> None:
        recognizer = RegexRecognizer(tokenize(r"a\]b]"))
        node = recognizer.set_items()
        self.assertEqual(node.name, "SITEMS")
        self.assertEqual(len(node.children), 3)
        self.assertEqual(recognizer.stream.peek().typ, TokenType.RSET)

    def test_set_items_rejects_empty_and_unterminated_input(self) -> None:
        with self.assertRaises(RecognitionError):
            RegexRecognizer(tokenize("]")).set_items()
        with self.assertRaises(RecognitionError):
            RegexRecognizer(tokenize("ab")).set_items()

    def test_malformed_escape_is_rejected(self) -> None:
        with self.assertRaises(RecognitionError):
            RegexRecognizer(tokenize(r"\q")).char_or_meta()

    def test_tree_rendering_is_stable(self) -> None:
        node = RegexRecognizer(tokenize(r"\|")).char_or_meta()
        self.assertEqual(
            RegexRecognizer.render(node),
            "CHAR_OR_META\n    \\ BSLASH\n    | VERT",
        )


if __name__ == "__main__":
    unittest.main()
