"""Tokenization interface for regular-expression input.

The scanner implementation is introduced in Issue 2. This module provides
the stable interface used by the command-line entry point and recognizer.
"""

from collections.abc import Iterator


def tokenize(expression: str) -> Iterator[str]:
    """Yield the input characters in order.

    Issue 2 will replace this bootstrap implementation with the assignment's
    token types and lexeme handling.
    """

    yield from expression
