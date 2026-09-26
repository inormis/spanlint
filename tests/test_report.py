from __future__ import annotations

import json

from spanlint.report import render_json, render_text
from spanlint.validate import Finding


def test_render_json_empty() -> None:
    out = render_json([])
    assert out.endswith("\n")
    assert json.loads(out) == {"findings": []}


def test_render_json_single_finding() -> None:
    findings = [Finding(rule="r", target="t", message="m")]
    parsed = json.loads(render_json(findings))
    assert parsed == {"findings": [{"rule": "r", "target": "t", "message": "m"}]}


def test_render_json_preserves_order() -> None:
    findings = [
        Finding(rule="a", target="x", message="1"),
        Finding(rule="b", target="y", message="2"),
        Finding(rule="c", target="z", message="3"),
    ]
    parsed = json.loads(render_json(findings))
    assert [f["rule"] for f in parsed["findings"]] == ["a", "b", "c"]


def test_render_json_is_indented() -> None:
    out = render_json([Finding(rule="r", target="t", message="m")])
    assert "\n  " in out


def test_render_text_empty() -> None:
    assert render_text([]) == "no findings\n"


def test_render_text_single_finding() -> None:
    out = render_text([Finding(rule="r", target="t", message="m")])
    assert out == "t: m [r]\n1 finding\n"


def test_render_text_multiple_findings() -> None:
    findings = [
        Finding(rule="a", target="x", message="1"),
        Finding(rule="b", target="y", message="2"),
    ]
    assert render_text(findings) == "x: 1 [a]\ny: 2 [b]\n2 findings\n"
