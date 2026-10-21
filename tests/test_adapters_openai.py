from __future__ import annotations

from pathlib import Path

import pytest

from spanlint.adapters.openai import is_openai_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE = FIXTURES / "openai" / "chat_completion.json"
TRACELOOP_FIXTURES = [
    FIXTURES / "llamaindex" / "chat_engine_traceloop.json",
    FIXTURES / "traceloop" / "workflow.json",
]


def _bare(**kw: object) -> Span:
    defaults: dict[str, object] = {
        "name": "s",
        "kind": SpanKind.CLIENT,
        "start_time_unix_nano": 0,
        "end_time_unix_nano": 1,
    }
    defaults.update(kw)
    return Span(**defaults)  # type: ignore[arg-type]


def test_identifies_openai_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURE)
    assert len(spans) == 1
    assert is_openai_span(spans[0])


@pytest.mark.parametrize("fixture", TRACELOOP_FIXTURES, ids=lambda p: p.parent.name)
def test_claims_only_the_openai_call_in_traceloop_fixtures(fixture: Path) -> None:
    spans = parse_otlp_json_file(fixture)
    assert [span.name for span in spans if is_openai_span(span)] == ["openai.chat"]


def test_identifies_by_contrib_scope_name() -> None:
    span = _bare(instrumentation_scope="opentelemetry.instrumentation.openai_v2")
    assert is_openai_span(span)


def test_identifies_by_traceloop_scope_name() -> None:
    span = _bare(instrumentation_scope="opentelemetry.instrumentation.openai.v1")
    assert is_openai_span(span)


def test_identifies_by_gen_ai_system_attribute() -> None:
    span = _bare(attributes={"gen_ai.system": "openai"})
    assert is_openai_span(span)


def test_identifies_by_provider_name_attribute() -> None:
    span = _bare(attributes={"gen_ai.provider.name": "openai"})
    assert is_openai_span(span)


def test_rejects_unrelated_scope_and_system() -> None:
    span = _bare(
        instrumentation_scope="opentelemetry.instrumentation.requests",
        attributes={"gen_ai.system": "anthropic", "gen_ai.provider.name": "anthropic"},
    )
    assert not is_openai_span(span)


def test_rejects_span_with_no_signal() -> None:
    assert not is_openai_span(_bare())
