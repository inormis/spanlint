from __future__ import annotations

from pathlib import Path

import pytest

from spanlint.adapters.traceloop import is_traceloop_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURE = Path(__file__).parent / "fixtures" / "traceloop" / "workflow.json"


def _bare(**kw: object) -> Span:
    defaults: dict[str, object] = {
        "name": "s",
        "kind": SpanKind.INTERNAL,
        "start_time_unix_nano": 0,
        "end_time_unix_nano": 1,
    }
    defaults.update(kw)
    return Span(**defaults)  # type: ignore[arg-type]


def test_identifies_only_the_decorator_spans_in_fixture() -> None:
    # arrange
    spans = parse_otlp_json_file(FIXTURE)
    assert len(spans) == 3
    # act
    matched = sorted(span.name for span in spans if is_traceloop_span(span))
    # assert
    assert matched == ["ask.task", "greet.workflow"]


def test_identifies_by_sdk_scope_name() -> None:
    assert is_traceloop_span(_bare(instrumentation_scope="traceloop.tracer"))


@pytest.mark.parametrize(
    "scope",
    [
        "opentelemetry.instrumentation.openai.v1",
        "opentelemetry.instrumentation.langchain",
    ],
)
def test_leaves_traceloop_instrumentation_spans_to_framework_adapters(scope: str) -> None:
    span = _bare(
        instrumentation_scope=scope,
        attributes={"traceloop.span.kind": "workflow", "traceloop.workflow.name": "w"},
    )
    assert not is_traceloop_span(span)


def test_rejects_span_with_no_signal() -> None:
    assert not is_traceloop_span(_bare())
