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

The scanner and recognizer currently expose the interfaces needed by the
upcoming implementation issues. Grammar and concrete syntax tree behavior
will be implemented incrementally.
