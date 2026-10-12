import regexTokenizer as tk


class RegexParser:
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.position = 0

    def peek(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def next(self):
        token = self.peek()
        if token is not None:
            self.position += 1
        return token

    def print_node(self, name, level):
        print("    " * level + name)

    def print_token(self, level):
        token = self.next()
        print("    " * level + token.value + " " + token.typ)

    def parse_re(self, level):
        self.print_node("RE", level)
        self.parse_simple_re(level + 1)
        while self.peek() is not None and self.peek().typ == "VERT":
            self.print_token(level + 1)
            self.parse_simple_re(level + 1)

    def parse_simple_re(self, level):
        self.print_node("S_RE", level)
        if not self.starts_elementary_re():
            raise ValueError("expected a basic regular expression")
        while self.starts_elementary_re():
            self.parse_basic_re(level + 1)

    def parse_basic_re(self, level):
        self.print_node("B_RE", level)
        self.parse_elementary_re(level + 1)
        if self.peek() is not None and self.peek().typ in ("STAR", "PLUS", "QMARK"):
            self.print_token(level + 1)

    def parse_elementary_re(self, level):
        self.print_node("E_RE", level)
        token = self.peek()
        if token is None:
            raise ValueError("expected an elementary regular expression")
        if token.typ == "LPAREN":
            self.print_token(level + 1)
            self.parse_re(level + 1)
            self.expect("RPAREN", level + 1)
        elif token.typ == "PERIOD":
            self.print_token(level + 1)
        elif token.typ in ("LPOSSET", "LNEGSET"):
            self.print_token(level + 1)
            self.parse_set_items(level + 1)
            self.expect("RSET", level + 1)
        else:
            self.parse_char_or_meta(level + 1)

    def parse_char_or_meta(self, level):
        self.print_node("CHAR_OR_META", level)
        token = self.peek()
        if token is not None and token.typ == "CHAR":
            self.print_token(level + 1)
        elif token is not None and token.typ == "BSLASH":
            self.print_token(level + 1)
            if self.peek() is None or self.peek().typ not in (
                "VERT", "STAR", "PLUS", "QMARK", "LPAREN", "RPAREN", "PERIOD",
                "LPOSSET", "LNEGSET", "RSET", "LANGLE", "RANGLE", "BSLASH"
            ):
                raise ValueError("expected a metacharacter after backslash")
            self.print_token(level + 1)
        else:
            raise ValueError("expected a character or escaped metacharacter")

    def parse_set_items(self, level):
        self.print_node("SITEMS", level)
        if self.peek() is None or self.peek().typ == "RSET":
            raise ValueError("expected a set item")
        while self.peek() is not None and self.peek().typ != "RSET":
            self.parse_char_or_meta(level + 1)

    def expect(self, token_type, level):
        if self.peek() is None or self.peek().typ != token_type:
            raise ValueError("expected " + token_type)
        self.print_token(level)

    def starts_elementary_re(self):
        return self.peek() is not None and self.peek().typ in (
            "CHAR", "BSLASH", "PERIOD", "LPAREN", "LPOSSET", "LNEGSET"
        )


expressions = ["two", "t|w|o", "[two]", "[^two]", "t(oo?|wo)", r"(\<(/?[^\>]+)\>)"]

for expression in expressions:
    print('Processing expression: "' + expression + '"')
    parser = RegexParser(tk.tokenize(expression))
    parser.parse_re(0)
    if parser.peek() is not None:
        raise ValueError("unexpected token: " + parser.peek().value)
