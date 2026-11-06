from __future__ import annotations

from pathlib import Path

import pytest

from spanlint.adapters.vercel_ai import is_vercel_ai_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURES = Path(__file__).parent / "fixtures" / "vercel_ai"


def _bare(**kw: object) -> Span:
    defaults: dict[str, object] = {
        "name": "s",
        "kind": SpanKind.INTERNAL,
        "start_time_unix_nano": 0,
        "end_time_unix_nano": 1,
    }
    defaults.update(kw)
    return Span(**defaults)  # type: ignore[arg-type]


def test_identifies_every_span_in_semconv_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURES / "generate_text_semconv.json")
    assert [span.name for span in spans if is_vercel_ai_span(span)] == [
        "chat gpt-4o-mini",
        "step 1",
        "invoke_agent gpt-4o-mini",
    ]


def test_identifies_every_span_in_legacy_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURES / "generate_text_legacy.json")
    assert [span.name for span in spans if is_vercel_ai_span(span)] == [
        "ai.generateText.doGenerate",
        "ai.generateText",
    ]


@pytest.mark.parametrize("scope", ["gen_ai", "ai"])
def test_identifies_by_scope_name(scope: str) -> None:
    assert is_vercel_ai_span(_bare(instrumentation_scope=scope))


def test_identifies_legacy_attributes_under_a_custom_tracer() -> None:
    span = _bare(
        instrumentation_scope="my-app",
        attributes={"ai.operationId": "ai.generateText", "ai.model.id": "gpt-4o-mini"},
    )
    assert is_vercel_ai_span(span)


def test_rejects_semconv_attributes_under_another_scope() -> None:
    span = _bare(
        instrumentation_scope="opentelemetry.instrumentation.openai_v2",
        attributes={"gen_ai.provider.name": "openai", "gen_ai.operation.name": "chat"},
    )
    assert not is_vercel_ai_span(span)


def test_rejects_span_with_no_signal() -> None:
    assert not is_vercel_ai_span(_bare())
