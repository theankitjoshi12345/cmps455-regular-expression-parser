"""Scanner and token stream for regular-expression input."""

from __future__ import annotations

import re
from collections import namedtuple
from collections.abc import Iterable, Iterator
from typing import Optional


class TokenType:
    """Names emitted by :func:`tokenize`."""

    VERT = "VERT"
    STAR = "STAR"
    PLUS = "PLUS"
    QMARK = "QMARK"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    PERIOD = "PERIOD"
    LPOSSET = "LPOSSET"
    LNEGSET = "LNEGSET"
    RSET = "RSET"
    LANGLE = "LANGLE"
    RANGLE = "RANGLE"
    BSLASH = "BSLASH"
    EOL = "EOL"
    CHAR = "CHAR"
    ERROR = "ERROR"

    # Descriptive aliases make the delimiters easier to use from a parser.
    LSET = LPOSSET
    NSET = LNEGSET
    POSITIVE_SET = LPOSSET
    NEGATIVE_SET = LNEGSET
    BACKSLASH = BSLASH


Token = namedtuple("Token", ["typ", "value", "line", "column"])


_SINGLE_CHARACTER_TOKENS = {
    "|": TokenType.VERT,
    "*": TokenType.STAR,
    "+": TokenType.PLUS,
    "?": TokenType.QMARK,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ".": TokenType.PERIOD,
    "[": TokenType.LPOSSET,
    "]": TokenType.RSET,
    "<": TokenType.LANGLE,
    ">": TokenType.RANGLE,
    "\\": TokenType.BSLASH,
}
_TOKEN_PATTERN = re.compile(r"\[\^|[|*+?().\[\]<>\\\n]|[^\s]")


def tokenize(code: str) -> Iterator[Token]:
    """Yield regular-expression tokens with one-based lines and columns.

    Spaces and tabs are ignored. ``[^`` is recognized as one negative-set
    delimiter; all other grammar symbols are emitted as individual tokens.
    Characters outside the grammar are emitted as ``ERROR`` tokens so callers
    can report the complete input rather than losing the remaining stream.
    """

    line = 1
    line_start = 0
    for match in _TOKEN_PATTERN.finditer(code):
        value = match.group(0)
        column = match.start() - line_start
        if value == "\n":
            yield Token(TokenType.EOL, value, line, column)
            line += 1
            line_start = match.end()
            continue

        if value == "[^":
            token_type = TokenType.LNEGSET
        elif value in _SINGLE_CHARACTER_TOKENS:
            token_type = _SINGLE_CHARACTER_TOKENS[value]
        elif value.isspace():
            continue
        elif value.isprintable():
            token_type = TokenType.CHAR
        else:
            token_type = TokenType.ERROR
        yield Token(token_type, value, line, column)


class TokenStream:
    """Peek and advance through a finite token sequence."""

    def __init__(self, tokens: Iterable[Token]) -> None:
        self._tokens = tuple(tokens)
        self._position = 0

    def peek(self, offset: int = 0) -> Optional[Token]:
        """Return a future token without consuming it."""

        if offset < 0:
            raise ValueError("peek offset must not be negative")
        index = self._position + offset
        if index >= len(self._tokens):
            return None
        return self._tokens[index]

    def advance(self) -> Optional[Token]:
        """Consume and return the next token, or ``None`` at end of input."""

        token = self.peek()
        if token is not None:
            self._position += 1
        return token

    def __iter__(self) -> Iterator[Token]:
        while (token := self.advance()) is not None:
            yield token


__all__ = ["Token", "TokenStream", "TokenType", "tokenize"]
