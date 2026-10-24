from __future__ import annotations

from pathlib import Path

from spanlint.adapters.meai import is_meai_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURES = Path(__file__).parent / "fixtures" / "meai"


def _bare(**kw: object) -> Span:
    defaults: dict[str, object] = {
        "name": "s",
        "kind": SpanKind.INTERNAL,
        "start_time_unix_nano": 0,
        "end_time_unix_nano": 1,
    }
    defaults.update(kw)
    return Span(**defaults)  # type: ignore[arg-type]


def test_identifies_the_span_in_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURES / "chat.json")
    assert [span.name for span in spans if is_meai_span(span)] == ["chat gpt-4o-mini"]


def test_identifies_by_scope_name() -> None:
    assert is_meai_span(_bare(instrumentation_scope="Experimental.Microsoft.Extensions.AI"))


def test_rejects_same_attributes_under_another_scope() -> None:
    span = _bare(
        instrumentation_scope="opentelemetry.instrumentation.openai_v2",
        attributes={"gen_ai.provider.name": "openai", "gen_ai.operation.name": "chat"},
    )
    assert not is_meai_span(span)


def test_rejects_renamed_activity_source() -> None:
    span = _bare(
        instrumentation_scope="MyApp.Chat",
        attributes={"gen_ai.provider.name": "openai", "gen_ai.request.model": "gpt-4o-mini"},
    )
    assert not is_meai_span(span)


def test_rejects_span_with_no_signal() -> None:
    assert not is_meai_span(_bare())
