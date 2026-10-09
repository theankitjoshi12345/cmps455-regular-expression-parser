"""Recursive-descent recognizer interface for regular expressions."""

from collections.abc import Iterable


class RegexRecognizer:
    """Recognize one regular expression.

    The grammar methods will be implemented in Issues 3–7. Keeping this
    class separate from the scanner lets those changes remain focused.
    """

    def __init__(self, tokens: Iterable[str]) -> None:
        self.tokens = tuple(tokens)

    def recognize(self) -> bool:
        """Return whether the bootstrap input can be processed.

        The complete grammar validation is intentionally deferred to the
        scanner and grammar issues.
        """

        return bool(self.tokens)
