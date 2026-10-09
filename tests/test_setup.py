"""Smoke tests for the Issue 1 project structure."""

import unittest

from regex_parser.main import DEFAULT_EXPRESSIONS, run
from regex_parser.recognizer import RegexRecognizer
from regex_parser.scanner import tokenize


class ProjectSetupTests(unittest.TestCase):
    def test_default_expressions_are_available(self) -> None:
        self.assertEqual(len(DEFAULT_EXPRESSIONS), 6)

    def test_scanner_and_recognizer_interfaces_are_separate(self) -> None:
        tokens = tokenize("two")
        self.assertTrue(RegexRecognizer(tokens).recognize())

    def test_run_processes_an_expression(self) -> None:
        self.assertEqual(run(("two",)), 0)


if __name__ == "__main__":
    unittest.main()
