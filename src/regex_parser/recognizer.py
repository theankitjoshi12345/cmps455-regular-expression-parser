"""Recursive-descent recognizer for the CMPS 455 regular-expression grammar."""

from __future__ import annotations

from collections.abc import Iterable

from .scanner import Token, TokenStream, TokenType


class RecognitionError(ValueError):
    """Raised when the input does not match the assignment grammar."""


class RegexRecognizer:
    """Recognize and print a concrete syntax tree during recursive descent."""

    def __init__(self, tokens: Iterable[Token]) -> None:
        self.stream = tokens if isinstance(tokens, TokenStream) else TokenStream(tokens)

    def parse(self) -> None:
        """Parse one complete expression and print its tree."""

        self.parse_regular_expression(0)
        trailing_token = self.stream.peek()
        if trailing_token is not None:
            self._raise_error(f"unexpected trailing {trailing_token.typ}", trailing_token)

    def parse_regular_expression(self, indentation_level: int) -> None:
        """Parse ``<re> ::= <simple-re> { '|' <simple-re> }``."""

        self._print_node("RE", indentation_level)
        self.parse_simple_regular_expression(indentation_level + 1)

        while self.stream.peek() is not None and self.stream.peek().typ == TokenType.VERT:
            self._print_token(self.stream.advance(), indentation_level + 1)
            self.parse_simple_regular_expression(indentation_level + 1)

    def parse_simple_regular_expression(self, indentation_level: int) -> None:
        """Parse ``<simple-re> ::= <basic-re> { <basic-re> }``."""

        self._print_node("S_RE", indentation_level)
        if not self._starts_elementary():
            self._raise_expected("basic regular expression")

        while self._starts_elementary():
            self.parse_basic_regular_expression(indentation_level + 1)

    def parse_basic_regular_expression(self, indentation_level: int) -> None:
        """Parse ``<basic-re> ::= <elementary-re> [ '*' | '+' | '?' ]``."""

        self._print_node("B_RE", indentation_level)
        if self.stream.peek() is not None and self.stream.peek().typ in _QUANTIFIERS:
            self._raise_expected("elementary regular expression")

        self.parse_elementary_regular_expression(indentation_level + 1)
        next_token = self.stream.peek()
        if next_token is not None and next_token.typ in _QUANTIFIERS:
            self._print_token(self.stream.advance(), indentation_level + 1)
            next_token = self.stream.peek()
            if next_token is not None and next_token.typ in _QUANTIFIERS:
                self._raise_error("repeated quantifier", next_token)

    def parse_elementary_regular_expression(self, indentation_level: int) -> None:
        """Parse one of the five ``<elementary-re>`` alternatives."""

        self._print_node("E_RE", indentation_level)
        current_token = self.stream.peek()
        if current_token is None:
            self._raise_expected("elementary regular expression")

        if current_token.typ == TokenType.LPAREN:
            self._print_token(self.stream.advance(), indentation_level + 1)
            self.parse_regular_expression(indentation_level + 1)
            closing_token = self.stream.peek()
            if closing_token is None or closing_token.typ != TokenType.RPAREN:
                self._raise_expected("closing parenthesis")
            self._print_token(self.stream.advance(), indentation_level + 1)
            return

        if current_token.typ == TokenType.PERIOD:
            self._print_token(self.stream.advance(), indentation_level + 1)
            return

        if current_token.typ in (TokenType.LPOSSET, TokenType.LNEGSET):
            self._print_token(self.stream.advance(), indentation_level + 1)
            self.parse_set_items(indentation_level + 1)
            closing_token = self.stream.peek()
            if closing_token is None or closing_token.typ != TokenType.RSET:
                self._raise_expected("closing set bracket")
            self._print_token(self.stream.advance(), indentation_level + 1)
            return

        if current_token.typ in (TokenType.CHAR, TokenType.BSLASH):
            self.parse_character_or_metacharacter(indentation_level + 1)
            return

        self._raise_expected("elementary regular expression")

    def parse_character_or_metacharacter(
        self, indentation_level: int, allow_unescaped_metacharacter: bool = False
    ) -> None:
        """Parse ``<char-or-meta>`` and print its token leaves."""

        self._print_node("CHAR_OR_META", indentation_level)
        current_token = self.stream.peek()
        if current_token is None:
            self._raise_expected("character or metacharacter")

        if current_token.typ == TokenType.CHAR:
            self._print_token(self.stream.advance(), indentation_level + 1)
            return

        if (
            allow_unescaped_metacharacter
            and current_token.typ in _UNESCAPED_SET_METACHARACTERS
        ):
            self._print_token(self.stream.advance(), indentation_level + 1)
            return

        if current_token.typ == TokenType.BSLASH:
            self._print_token(self.stream.advance(), indentation_level + 1)
            next_token = self.stream.peek()
            if next_token is None or next_token.typ not in _METACHARACTERS:
                self._raise_expected("metacharacter after backslash")
            self._print_token(self.stream.advance(), indentation_level + 1)
            return

        self._raise_expected("character or metacharacter")

    def parse_set_items(self, indentation_level: int) -> None:
        """Parse ``<set-items> ::= <char-or-meta> { <char-or-meta> }``."""

        self._print_node("SITEMS", indentation_level)
        if self.stream.peek() is None or self.stream.peek().typ == TokenType.RSET:
            self._raise_expected("set item")

        while self.stream.peek() is not None and self.stream.peek().typ != TokenType.RSET:
            self.parse_character_or_metacharacter(
                indentation_level + 1, allow_unescaped_metacharacter=True
            )

    def _starts_elementary(self) -> bool:
        current_token = self.stream.peek()
        return current_token is not None and current_token.typ in {
            TokenType.CHAR,
            TokenType.BSLASH,
            TokenType.PERIOD,
            TokenType.LPAREN,
            TokenType.LPOSSET,
            TokenType.LNEGSET,
        }

    @staticmethod
    def _print_node(label: str, indentation_level: int) -> None:
        print(f"{'    ' * indentation_level}{label}")

    @staticmethod
    def _print_token(token: Token | None, indentation_level: int) -> None:
        if token is not None:
            print(f"{'    ' * indentation_level}{token.value} {token.typ}")

    def _raise_expected(self, expected: str) -> None:
        token = self.stream.peek()
        if token is None:
            raise RecognitionError(f"expected {expected}, found end of input")
        self._raise_error(f"expected {expected}", token)

    @staticmethod
    def _raise_error(message: str, token: Token) -> None:
        raise RecognitionError(
            f"{message}; found {token.typ} at line {token.line}, column {token.column}"
        )


_QUANTIFIERS = frozenset({TokenType.STAR, TokenType.PLUS, TokenType.QMARK})
_METACHARACTERS = frozenset(
    {
        TokenType.VERT,
        TokenType.STAR,
        TokenType.PLUS,
        TokenType.QMARK,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.PERIOD,
        TokenType.LPOSSET,
        TokenType.LNEGSET,
        TokenType.RSET,
        TokenType.LANGLE,
        TokenType.RANGLE,
        TokenType.BSLASH,
    }
)
_UNESCAPED_SET_METACHARACTERS = _METACHARACTERS - {TokenType.RSET, TokenType.BSLASH}


__all__ = ["RecognitionError", "RegexRecognizer"]
