from __future__ import annotations

import json
from pathlib import Path

from spanlint.conformance import run_matrix
from spanlint.registry import Registry, load_registry

FIXTURES = Path(__file__).parent / "fixtures"

BUNDLED = [
    "langchain",
    "langfuse",
    "litellm",
    "llamaindex",
    "meai",
    "openai",
    "semantic_kernel",
    "traceloop",
    "vercel_ai",
]


def _registry() -> Registry:
    return load_registry(FIXTURES / "gen_ai.yaml")


def _span(name: str, attributes: dict[str, dict[str, object]]) -> dict[str, object]:
    return {
        "name": name,
        "kind": 3,
        "startTimeUnixNano": "0",
        "endTimeUnixNano": "1",
        "attributes": [{"key": k, "value": v} for k, v in attributes.items()],
    }


def _write_export(path: Path, scope: str, spans: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    export = {"resourceSpans": [{"scopeSpans": [{"scope": {"name": scope}, "spans": spans}]}]}
    path.write_text(json.dumps(export))


def test_matrix_covers_every_bundled_framework_in_order() -> None:
    matrix = run_matrix(FIXTURES, _registry())
    assert list(matrix) == BUNDLED


def test_rules_within_a_framework_are_sorted() -> None:
    matrix = run_matrix(FIXTURES, _registry())
    assert all(list(counts) == sorted(counts) for counts in matrix.values())


def test_counts_findings_per_rule_over_claimed_spans_only(tmp_path: Path) -> None:
    # arrange
    broken: dict[str, dict[str, object]] = {
        "gen_ai.system": {"stringValue": "openai"},
        "gen_ai.request.model": {"intValue": "4"},
    }
    _write_export(
        tmp_path / "meai" / "a.json",
        "Experimental.Microsoft.Extensions.AI",
        [_span("chat", broken), _span("chat", broken)],
    )
    _write_export(tmp_path / "meai" / "b.json", "something.else", [_span("chat", broken)])
    # act
    matrix = run_matrix(tmp_path, _registry())
    # assert
    assert matrix == {"meai": {"gen_ai.request.model.type": 2}}


def test_claimed_span_without_gen_ai_attributes_is_counted(tmp_path: Path) -> None:
    span = _span("greet", {"langfuse.observation.type": {"stringValue": "span"}})
    _write_export(tmp_path / "langfuse" / "a.json", "langfuse-sdk", [span])
    assert run_matrix(tmp_path, _registry()) == {"langfuse": {"gen_ai.attributes.missing": 1}}


def test_frameworks_without_fixtures_are_left_out(tmp_path: Path) -> None:
    span = _span("chat", {"gen_ai.system": {"stringValue": "openai"}})
    _write_export(tmp_path / "openai" / "a.json", "openai", [span])
    assert run_matrix(tmp_path, _registry()) == {"openai": {}}
