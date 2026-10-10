"""Allow the package to be run with ``python -m regex_parser``."""

from .main import main


if __name__ == "__main__":
    raise SystemExit(main())
