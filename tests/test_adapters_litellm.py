from __future__ import annotations

from pathlib import Path

import pytest

from spanlint.adapters.litellm import is_litellm_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURES = Path(__file__).parent / "fixtures" / "litellm"


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
    spans = parse_otlp_json_file(FIXTURES / "completion_native.json")
    assert len(spans) == 2
    assert all(is_litellm_span(span) for span in spans)


def test_identifies_the_span_in_traceloop_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURES / "completion_traceloop.json")
    assert [span.name for span in spans if is_litellm_span(span)] == ["litellm.chat"]


@pytest.mark.parametrize(
    "scope",
    [
        "litellm",
        "opentelemetry.instrumentation.litellm",
        "openinference.instrumentation.litellm",
    ],
)
def test_identifies_by_scope_name(scope: str) -> None:
    assert is_litellm_span(_bare(instrumentation_scope=scope))


def test_rejects_openai_span_routed_through_litellm_provider() -> None:
    span = _bare(
        instrumentation_scope="opentelemetry.instrumentation.openai.v1",
        attributes={"gen_ai.provider.name": "openai", "gen_ai.system": "openai"},
    )
    assert not is_litellm_span(span)


def test_rejects_span_with_no_signal() -> None:
    assert not is_litellm_span(_bare())
