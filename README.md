# CMPS455 Regular-Expression Parser

Python implementation of the CMPS455 regular-expression scanner and
recursive-descent recognizer. The project follows the grammar and output
requirements in
[CMPS455_Regular_Expression_Parser_Instructions.pdf](./CMPS455_Regular_Expression_Parser_Instructions.pdf).

## Requirements

- Python 3.9 or newer

The initial project setup has no third-party runtime dependencies. The
scanner and recognizer are intentionally separate modules so their
implementations can be developed independently.

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run

Process the assignment's sample expressions:

```bash
python -m regex_parser
```

Process expressions supplied on the command line:

```bash
python -m regex_parser 'two' 't|w|o' 't(oo?|wo)'
```

## Test

```bash
python -m unittest discover -s tests -v
```

The instructor-provided `Tokenizer.py` in the repository root is preserved as
reference material. The package scanner adapts its token-record and
source-location conventions for the regular-expression grammar without
executing the reference file's demonstration code on import.

The scanner exposes `Token`, `TokenType`, `tokenize`, and `TokenStream`.
`tokenize` preserves each token's lexeme and one-based line/zero-based column;
spaces and tabs are skipped, newlines produce `EOL`, and unsupported control
characters produce `ERROR`.

The recognizer exposes the grammar layers `char_or_meta`, `set_items`,
`elementary_re`, `basic_re`, `simple_re`, and `regular_expression`. Use
`RegexRecognizer.parse()` for a complete parse tree; it raises
`RecognitionError` with the offending token and source position for malformed
input. `recognize()` provides a boolean validation result, and
`ParseNode.render` renders the tree with four spaces per grammar level and
token leaves in `lexeme TOKEN_TYPE` form.

For example, `python -m regex_parser two` prints:

```text
Processing expression: "two"
RE
    S_RE
        B_RE
            E_RE
                t CHAR
        B_RE
            E_RE
                w CHAR
        B_RE
            E_RE
                o CHAR
```

Malformed input is reported with the token and source location, and the
process exits nonzero when any supplied expression is invalid.
