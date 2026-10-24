from __future__ import annotations

from pathlib import Path

import pytest

from spanlint.adapters.langfuse import is_langfuse_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURES = Path(__file__).parent / "fixtures" / "langfuse"


def _bare(**kw: object) -> Span:
    defaults: dict[str, object] = {
        "name": "s",
        "kind": SpanKind.INTERNAL,
        "start_time_unix_nano": 0,
        "end_time_unix_nano": 1,
    }
    defaults.update(kw)
    return Span(**defaults)  # type: ignore[arg-type]


def test_identifies_every_span_in_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURES / "observe_openai.json")
    assert len(spans) == 2
    assert all(is_langfuse_span(span) for span in spans)


def test_identifies_by_scope_name() -> None:
    assert is_langfuse_span(_bare(instrumentation_scope="langfuse-sdk"))


def test_rejects_foreign_span_carrying_propagated_langfuse_attributes() -> None:
    span = _bare(
        instrumentation_scope="opentelemetry.instrumentation.openai.v1",
        attributes={
            "langfuse.trace.name": "greet",
            "user.id": "u-1",
            "gen_ai.provider.name": "openai",
        },
    )
    assert not is_langfuse_span(span)


@pytest.mark.parametrize("scope", ["langfuse", "langsmith"])
def test_rejects_lookalike_scopes(scope: str) -> None:
    assert not is_langfuse_span(_bare(instrumentation_scope=scope))


def test_rejects_span_with_no_signal() -> None:
    assert not is_langfuse_span(_bare())
