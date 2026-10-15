from __future__ import annotations

from pathlib import Path

import pytest

from spanlint.adapters.langchain import is_langchain_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURE = Path(__file__).parent / "fixtures" / "langchain" / "chain.json"


def _bare(**kw: object) -> Span:
    defaults: dict[str, object] = {
        "name": "s",
        "kind": SpanKind.INTERNAL,
        "start_time_unix_nano": 0,
        "end_time_unix_nano": 1,
    }
    defaults.update(kw)
    return Span(**defaults)  # type: ignore[arg-type]


def test_identifies_every_span_in_langchain_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURE)
    assert len(spans) == 3
    assert all(is_langchain_span(span) for span in spans)


def test_identifies_by_traceloop_scope_name() -> None:
    span = _bare(instrumentation_scope="opentelemetry.instrumentation.langchain")
    assert is_langchain_span(span)


def test_identifies_by_openinference_scope_name() -> None:
    span = _bare(instrumentation_scope="openinference.instrumentation.langchain")
    assert is_langchain_span(span)


@pytest.mark.parametrize("provider", ["langchain", "langgraph"])
def test_identifies_by_provider_name_attribute(provider: str) -> None:
    span = _bare(attributes={"gen_ai.provider.name": provider})
    assert is_langchain_span(span)


def test_rejects_unrelated_scope_and_provider() -> None:
    span = _bare(
        instrumentation_scope="opentelemetry.instrumentation.openai_v2",
        attributes={"gen_ai.provider.name": "openai"},
    )
    assert not is_langchain_span(span)


def test_rejects_span_with_no_signal() -> None:
    assert not is_langchain_span(_bare())
