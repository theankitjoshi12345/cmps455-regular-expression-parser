"""Recursive-descent recognizer rules for regular expressions."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import List, Optional

from .scanner import Token, TokenStream, TokenType


class RecognitionError(ValueError):
    """Raised when a token sequence violates a recognizer rule."""


@dataclass(frozen=True)
class ParseNode:
    """A small concrete parse-tree node used by the Issue 3 rules."""

    name: str
    token: Optional[Token] = None
    children: tuple["ParseNode", ...] = ()

    def lines(self, depth: int = 0) -> List[str]:
        indent = "    " * depth
        if self.token is not None:
            return [f"{indent}{self.token.value} {self.token.typ}"]
        result = [f"{indent}{self.name}"]
        for child in self.children:
            result.extend(child.lines(depth + 1))
        return result


_ESCAPABLE_TYPES = frozenset(
    {
        TokenType.VERT,
        TokenType.STAR,
        TokenType.PLUS,
        TokenType.QMARK,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.PERIOD,
        TokenType.LSET,
        TokenType.NSET,
        TokenType.RSET,
        TokenType.LANGLE,
        TokenType.RANGLE,
        TokenType.BSLASH,
    }
)


class RegexRecognizer:
    """Recognize the regular-expression grammar using recursive descent."""

    def __init__(self, tokens: Iterable[Token]) -> None:
        self.stream = (
            tokens if isinstance(tokens, TokenStream) else TokenStream(tokens)
        )

    def recognize(self) -> bool:
        """Return whether the complete token stream is a valid expression."""

        try:
            self.parse()
        except RecognitionError:
            return False
        return True

    def parse(self) -> ParseNode:
        """Parse one complete regular expression and reject trailing input."""

        node = self.regular_expression()
        token = self.stream.peek()
        if token is not None:
            raise RecognitionError(
                f"unexpected trailing token {token.typ} at "
                f"line {token.line}, column {token.column}"
            )
        return node

    def char_or_meta(self, *, in_set: bool = False) -> ParseNode:
        """Parse ``<char-or-meta>`` and consume its tokens."""

        token = self.stream.peek()
        if token is None:
            raise RecognitionError("expected CHAR_OR_META, found end of input")
        if token.typ == TokenType.CHAR:
            self.stream.advance()
            return ParseNode("CHAR_OR_META", token=token)
        if in_set and token.typ in (TokenType.LANGLE, TokenType.RANGLE):
            self.stream.advance()
            return ParseNode("CHAR_OR_META", token=token)
        if token.typ == TokenType.BSLASH:
            slash = self.stream.advance()
            escaped = self.stream.peek()
            if escaped is None or escaped.typ not in _ESCAPABLE_TYPES:
                raise RecognitionError(
                    "backslash must be followed by an escapable metacharacter"
                )
            self.stream.advance()
            return ParseNode(
                "CHAR_OR_META",
                children=(
                    ParseNode("BSLASH", token=slash),
                    ParseNode("META", token=escaped),
                ),
            )
        raise RecognitionError(
            f"expected CHAR or escaped metacharacter, found {token.typ}"
        )

    def set_items(self) -> ParseNode:
        """Parse one or more ``<set-items>`` until the caller sees RSET."""

        items: list[ParseNode] = []
        while self.stream.peek() is not None:
            if self.stream.peek().typ == TokenType.RSET:
                break
            items.append(self.char_or_meta(in_set=True))
        if not items:
            raise RecognitionError("set-items requires at least one item")
        if self.stream.peek() is None:
            raise RecognitionError("set-items is unterminated")
        return ParseNode("SITEMS", children=tuple(items))

    def elementary_re(self) -> ParseNode:
        """Parse one ``<elementary-re>`` alternative."""

        token = self.stream.peek()
        if token is None:
            raise RecognitionError("expected elementary regular expression")

        if token.typ == TokenType.LPAREN:
            left = self.stream.advance()
            contents = self.regular_expression()
            right = self.stream.peek()
            if right is None or right.typ != TokenType.RPAREN:
                raise RecognitionError("parenthesized expression is unterminated")
            self.stream.advance()
            return ParseNode(
                "E_RE",
                children=(
                    ParseNode("LPAREN", token=left),
                    contents,
                    ParseNode("RPAREN", token=right),
                ),
            )

        if token.typ == TokenType.PERIOD:
            self.stream.advance()
            return ParseNode("E_RE", children=(ParseNode("PERIOD", token=token),))

        if token.typ in (TokenType.CHAR, TokenType.BSLASH):
            return ParseNode("E_RE", children=(self.char_or_meta(),))

        if token.typ in (TokenType.LSET, TokenType.NSET):
            left = self.stream.advance()
            items = self.set_items()
            right = self.stream.advance()
            if right is None:
                raise RecognitionError("set is unterminated")
            return ParseNode(
                "E_RE",
                children=(
                    ParseNode(token.typ, token=left),
                    items,
                    ParseNode(TokenType.RSET, token=right),
                ),
            )

        raise RecognitionError(
            f"expected elementary regular expression, found {token.typ}"
        )

    def elementaryRE(self) -> ParseNode:
        return self.elementary_re()

    def simple_re(self) -> ParseNode:
        """Parse one or more adjacent basic regular expressions."""

        basics: list[ParseNode] = []
        while self._starts_elementary():
            basics.append(self.basic_re())
        if not basics:
            self._raise_expected("basic regular expression")
        return ParseNode("S_RE", children=tuple(basics))

    def simpleRE(self) -> ParseNode:
        return self.simple_re()

    def regular_expression(self) -> ParseNode:
        """Parse one or more simple expressions separated by VERT."""

        alternatives = [self.simple_re()]
        while self.stream.peek() is not None:
            if self.stream.peek().typ != TokenType.VERT:
                break
            vertical = self.stream.advance()
            alternatives.append(
                ParseNode(TokenType.VERT, token=vertical)
            )
            alternatives.append(self.simple_re())
        return ParseNode("RE", children=tuple(alternatives))

    def regularExpression(self) -> ParseNode:
        return self.regular_expression()

    def basic_re(self) -> ParseNode:
        """Parse ``<basic-re>`` with an optional unary quantifier."""

        token = self.stream.peek()
        if token is not None and token.typ in _QUANTIFIER_TYPES:
            raise RecognitionError(
                f"quantifier {token.typ} must follow an elementary expression"
            )

        elementary = self.elementary_re()
        children = [elementary]
        quantifier = self.stream.peek()
        if quantifier is not None and quantifier.typ in _QUANTIFIER_TYPES:
            children.append(
                ParseNode(quantifier.typ, token=self.stream.advance())
            )
            repeated = self.stream.peek()
            if repeated is not None and repeated.typ in _QUANTIFIER_TYPES:
                raise RecognitionError(
                    "an elementary expression may have only one quantifier"
                )
        return ParseNode("B_RE", children=tuple(children))

    def basicRE(self) -> ParseNode:
        return self.basic_re()

    def _starts_elementary(self) -> bool:
        token = self.stream.peek()
        return token is not None and token.typ in {
            TokenType.CHAR,
            TokenType.BSLASH,
            TokenType.PERIOD,
            TokenType.LPAREN,
            TokenType.LSET,
            TokenType.NSET,
        }

    def _raise_expected(self, expected: str) -> None:
        token = self.stream.peek()
        if token is None:
            raise RecognitionError(f"expected {expected}, found end of input")
        raise RecognitionError(
            f"expected {expected}, found {token.typ} at "
            f"line {token.line}, column {token.column}"
        )

    # Grammar-style aliases keep the rule names visible to callers.
    def charOrMeta(self) -> ParseNode:
        return self.char_or_meta()

    def sitems(self) -> ParseNode:
        return self.set_items()

    @staticmethod
    def render(node: ParseNode) -> str:
        """Render a parse node using the assignment tree format."""

        return "\n".join(node.lines())


_QUANTIFIER_TYPES = frozenset(
    {TokenType.STAR, TokenType.PLUS, TokenType.QMARK}
)


__all__ = ["ParseNode", "RecognitionError", "RegexRecognizer"]
