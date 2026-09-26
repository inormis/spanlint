from __future__ import annotations

import argparse
import sys
from importlib.metadata import version


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    parser.parse_args(argv)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="spanlint")
    parser.add_argument("--version", action="version", version=version("spanlint"))
    return parser


if __name__ == "__main__":
    sys.exit(main())
