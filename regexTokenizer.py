import collections


Token = collections.namedtuple("Token", ["typ", "value"])


def tokenize(expression):
    """Generate tokens for a regular expression."""
    token_types = {
        "|": "VERT", "*": "STAR", "+": "PLUS", "?": "QMARK",
        "(": "LPAREN", ")": "RPAREN", ".": "PERIOD", "[": "LPOSSET",
        "]": "RSET", "<": "LANGLE", ">": "RANGLE", "\\": "BSLASH",
        "\n": "EOL",
    }
    index = 0
    while index < len(expression):
        character = expression[index]
        if expression[index:index + 2] == "[^":
            yield Token("LNEGSET", "[^")
            index += 2
        elif character in token_types:
            yield Token(token_types[character], character)
            index += 1
        elif character.isprintable() and not character.isspace():
            yield Token("CHAR", character)
            index += 1
        else:
            yield Token("ERROR", character)
            index += 1
