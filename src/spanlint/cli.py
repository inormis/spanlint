from __future__ import annotations

import argparse
import sys
from importlib.metadata import version
from pathlib import Path

from spanlint.otlp import parse_otlp_json_file
from spanlint.registry import load_registry
from spanlint.report import render_json, render_text
from spanlint.rules import DEFAULT_SPAN_RULES
from spanlint.validate import validate

_REGISTRY_PATH = Path(__file__).parent / "data" / "gen_ai.yaml"


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return _run_check(args)
    parser.print_help()
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="spanlint")
    parser.add_argument("--version", action="version", version=version("spanlint"))
    sub = parser.add_subparsers(dest="command")
    check = sub.add_parser("check", help="Validate an OTLP JSON file against GenAI semconv")
    check.add_argument("path", type=Path)
    check.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def _run_check(args: argparse.Namespace) -> int:
    spans = parse_otlp_json_file(args.path)
    registry = load_registry(_REGISTRY_PATH)
    findings = validate(spans, DEFAULT_SPAN_RULES, registry)
    rendered = render_json(findings) if args.format == "json" else render_text(findings)
    sys.stdout.write(rendered)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
