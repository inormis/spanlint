from pathlib import Path

from spanlint.model import AttributeValue, Span, SpanKind
from spanlint.registry import Registry, load_registry
from spanlint.rules import (
    gen_ai_operation_name_enum,
    gen_ai_request_model_type,
    gen_ai_response_model_type,
    gen_ai_system_required,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _registry() -> Registry:
    return load_registry(FIXTURES / "gen_ai.yaml")


def _span(attrs: dict[str, AttributeValue] | None = None) -> Span:
    return Span(
        name="chat",
        kind=SpanKind.CLIENT,
        start_time_unix_nano=0,
        end_time_unix_nano=1,
        attributes=dict(attrs or {}),
    )


def test_gen_ai_system_present_passes() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_system_required(span, _registry()) == []


def test_gen_ai_system_missing_on_gen_ai_span_is_flagged() -> None:
    span = _span({"gen_ai.request.model": "gpt-4"})
    findings = gen_ai_system_required(span, _registry())
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.system.required"
    assert findings[0].span == "chat"


def test_non_gen_ai_span_is_not_flagged() -> None:
    span = _span({"http.method": "GET"})
    assert gen_ai_system_required(span, _registry()) == []


def test_span_with_no_attributes_is_not_flagged() -> None:
    assert gen_ai_system_required(_span(), _registry()) == []


def test_operation_name_known_value_passes() -> None:
    span = _span({"gen_ai.operation.name": "chat"})
    assert gen_ai_operation_name_enum(span, _registry()) == []


def test_operation_name_unknown_value_is_flagged() -> None:
    span = _span({"gen_ai.operation.name": "chit_chat"})
    findings = gen_ai_operation_name_enum(span, _registry())
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.operation.name.enum"
    assert "chit_chat" in findings[0].message


def test_operation_name_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_operation_name_enum(span, _registry()) == []


def test_request_model_string_passes() -> None:
    span = _span({"gen_ai.request.model": "gpt-4"})
    assert gen_ai_request_model_type(span, _registry()) == []


def test_request_model_non_string_is_flagged() -> None:
    span = _span({"gen_ai.request.model": 42})
    findings = gen_ai_request_model_type(span, _registry())
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.request.model.type"


def test_request_model_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_request_model_type(span, _registry()) == []


def test_response_model_string_passes() -> None:
    span = _span({"gen_ai.response.model": "gpt-4o-2024-08-06"})
    assert gen_ai_response_model_type(span, _registry()) == []


def test_response_model_non_string_is_flagged() -> None:
    span = _span({"gen_ai.response.model": ["gpt-4"]})
    findings = gen_ai_response_model_type(span, _registry())
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.response.model.type"


def test_response_model_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_response_model_type(span, _registry()) == []
