"""Command-line entry point for the CMPS455 recognizer."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import Optional

from .recognizer import RecognitionError, RegexRecognizer
from .scanner import tokenize

DEFAULT_EXPRESSIONS = (
    "two",
    "t|w|o",
    "[two]",
    "[^two]",
    "t(oo?|wo)",
    r"(\<(/?[^\\>]+)\>)",
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Recognize regular expressions for the CMPS455 project."
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        help="regular expressions to process (defaults to assignment examples)",
    )
    return parser


def run(expressions: Sequence[str]) -> int:
    """Process expressions and return a command-line status code."""

    status = 0
    for expression in expressions:
        print(f'Processing expression: "{expression}"')
        try:
            tree = RegexRecognizer(tokenize(expression)).parse()
        except RecognitionError as error:
            print(f"not recognized: {error}")
            status = 1
        else:
            print(RegexRecognizer.render(tree))
    return status


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Parse command-line arguments and process the selected expressions."""

    args = build_parser().parse_args(argv)
    expressions = args.expressions or DEFAULT_EXPRESSIONS
    return run(expressions)


if __name__ == "__main__":
    raise SystemExit(main())
