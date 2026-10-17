from __future__ import annotations

from pathlib import Path

import pytest

from spanlint.adapters.llamaindex import is_llamaindex_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURES = Path(__file__).parent / "fixtures" / "llamaindex"


def _bare(**kw: object) -> Span:
    defaults: dict[str, object] = {
        "name": "s",
        "kind": SpanKind.INTERNAL,
        "start_time_unix_nano": 0,
        "end_time_unix_nano": 1,
    }
    defaults.update(kw)
    return Span(**defaults)  # type: ignore[arg-type]


def test_identifies_every_span_in_native_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURES / "chat_engine_native.json")
    assert len(spans) == 2
    assert all(is_llamaindex_span(span) for span in spans)


def test_leaves_the_openai_span_alone_in_traceloop_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURES / "chat_engine_traceloop.json")
    assert len(spans) == 2
    assert [span.name for span in spans if is_llamaindex_span(span)] == [
        "SimpleChatEngine.workflow"
    ]


@pytest.mark.parametrize(
    "scope",
    [
        "opentelemetry.instrumentation.llamaindex",
        "openinference.instrumentation.llama_index",
        "llamaindex.opentelemetry.tracer",
    ],
)
def test_identifies_by_scope_name(scope: str) -> None:
    assert is_llamaindex_span(_bare(instrumentation_scope=scope))


def test_rejects_unrelated_scope() -> None:
    span = _bare(
        instrumentation_scope="opentelemetry.instrumentation.openai.v1",
        attributes={"gen_ai.provider.name": "openai"},
    )
    assert not is_llamaindex_span(span)


def test_rejects_span_with_no_signal() -> None:
    assert not is_llamaindex_span(_bare())
