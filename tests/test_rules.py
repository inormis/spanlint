from pathlib import Path

from spanlint.model import AttributeValue, Event, InstrumentType, Metric, Span, SpanKind
from spanlint.registry import Registry, load_registry
from spanlint.rules import (
    gen_ai_choice_event_attribute_types,
    gen_ai_client_operation_duration_metric,
    gen_ai_client_token_usage_metric,
    gen_ai_deprecated_attribute_name,
    gen_ai_message_event_attribute_types,
    gen_ai_operation_name_enum,
    gen_ai_request_max_tokens_type,
    gen_ai_request_model_type,
    gen_ai_request_temperature_type,
    gen_ai_request_top_p_type,
    gen_ai_response_finish_reasons_type,
    gen_ai_response_id_type,
    gen_ai_response_model_type,
    gen_ai_system_required,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _registry() -> Registry:
    return load_registry(FIXTURES / "gen_ai.yaml")


def _span(
    attrs: dict[str, AttributeValue] | None = None,
    events: list[Event] | None = None,
) -> Span:
    return Span(
        name="chat",
        kind=SpanKind.CLIENT,
        start_time_unix_nano=0,
        end_time_unix_nano=1,
        attributes=dict(attrs or {}),
        events=list(events or []),
    )


def test_gen_ai_system_present_passes() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_system_required(span, _registry()) == []


def test_gen_ai_system_missing_on_gen_ai_span_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.request.model": "gpt-4"})
    # act
    findings = gen_ai_system_required(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.system.required"
    assert findings[0].target == "chat"


def test_non_gen_ai_span_is_not_flagged() -> None:
    span = _span({"http.method": "GET"})
    assert gen_ai_system_required(span, _registry()) == []


def test_span_with_no_attributes_is_not_flagged() -> None:
    assert gen_ai_system_required(_span(), _registry()) == []


def test_operation_name_known_value_passes() -> None:
    span = _span({"gen_ai.operation.name": "chat"})
    assert gen_ai_operation_name_enum(span, _registry()) == []


def test_operation_name_unknown_value_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.operation.name": "chit_chat"})
    # act
    findings = gen_ai_operation_name_enum(span, _registry())
    # assert
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
    # arrange
    span = _span({"gen_ai.request.model": 42})
    # act
    findings = gen_ai_request_model_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.request.model.type"


def test_request_model_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_request_model_type(span, _registry()) == []


def test_response_model_string_passes() -> None:
    span = _span({"gen_ai.response.model": "gpt-4o-2024-08-06"})
    assert gen_ai_response_model_type(span, _registry()) == []


def test_response_model_non_string_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.response.model": ["gpt-4"]})
    # act
    findings = gen_ai_response_model_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.response.model.type"


def test_response_model_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_response_model_type(span, _registry()) == []


def test_request_temperature_double_passes() -> None:
    span = _span({"gen_ai.request.temperature": 0.7})
    assert gen_ai_request_temperature_type(span, _registry()) == []


def test_request_temperature_non_double_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.request.temperature": "hot"})
    # act
    findings = gen_ai_request_temperature_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.request.temperature.type"


def test_request_temperature_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_request_temperature_type(span, _registry()) == []


def test_request_top_p_double_passes() -> None:
    span = _span({"gen_ai.request.top_p": 0.9})
    assert gen_ai_request_top_p_type(span, _registry()) == []


def test_request_top_p_non_double_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.request.top_p": "high"})
    # act
    findings = gen_ai_request_top_p_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.request.top_p.type"


def test_request_top_p_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_request_top_p_type(span, _registry()) == []


def test_request_max_tokens_int_passes() -> None:
    span = _span({"gen_ai.request.max_tokens": 256})
    assert gen_ai_request_max_tokens_type(span, _registry()) == []


def test_request_max_tokens_float_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.request.max_tokens": 256.0})
    # act
    findings = gen_ai_request_max_tokens_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.request.max_tokens.type"


def test_request_max_tokens_bool_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.request.max_tokens": True})
    # act
    findings = gen_ai_request_max_tokens_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.request.max_tokens.type"


def test_request_max_tokens_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_request_max_tokens_type(span, _registry()) == []


def test_response_id_string_passes() -> None:
    span = _span({"gen_ai.response.id": "chatcmpl-abc123"})
    assert gen_ai_response_id_type(span, _registry()) == []


def test_response_id_non_string_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.response.id": 42})
    # act
    findings = gen_ai_response_id_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.response.id.type"


def test_response_id_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_response_id_type(span, _registry()) == []


def test_response_finish_reasons_list_passes() -> None:
    span = _span({"gen_ai.response.finish_reasons": ["stop", "length"]})
    assert gen_ai_response_finish_reasons_type(span, _registry()) == []


def test_response_finish_reasons_bare_string_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.response.finish_reasons": "stop"})
    # act
    findings = gen_ai_response_finish_reasons_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.response.finish_reasons.type"


def test_response_finish_reasons_list_of_ints_is_flagged() -> None:
    # arrange
    span = _span({"gen_ai.response.finish_reasons": [1, 2]})
    # act
    findings = gen_ai_response_finish_reasons_type(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.response.finish_reasons.type"


def test_response_finish_reasons_missing_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_response_finish_reasons_type(span, _registry()) == []


def _event(name: str, attrs: dict[str, AttributeValue] | None = None) -> Event:
    return Event(name=name, timestamp_unix_nano=0, attributes=dict(attrs or {}))


def test_user_message_event_with_valid_system_passes() -> None:
    span = _span(events=[_event("gen_ai.user.message", {"gen_ai.system": "openai"})])
    assert gen_ai_message_event_attribute_types(span, _registry()) == []


def test_system_message_event_with_valid_system_passes() -> None:
    span = _span(events=[_event("gen_ai.system.message", {"gen_ai.system": "anthropic"})])
    assert gen_ai_message_event_attribute_types(span, _registry()) == []


def test_user_message_event_with_non_string_system_is_flagged() -> None:
    # arrange
    span = _span(events=[_event("gen_ai.user.message", {"gen_ai.system": True})])
    # act
    findings = gen_ai_message_event_attribute_types(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.system.type"
    assert "gen_ai.user.message" in findings[0].message


def test_message_event_with_wrong_typed_known_attribute_is_flagged() -> None:
    # arrange
    span = _span(events=[_event("gen_ai.system.message", {"gen_ai.request.max_tokens": True})])
    # act
    findings = gen_ai_message_event_attribute_types(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.request.max_tokens.type"


def test_non_message_event_is_not_scanned() -> None:
    span = _span(events=[_event("custom.event", {"gen_ai.system": 123})])
    assert gen_ai_message_event_attribute_types(span, _registry()) == []


def test_span_with_no_events_is_not_flagged() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_message_event_attribute_types(span, _registry()) == []


def test_message_event_with_unknown_attribute_is_not_flagged() -> None:
    span = _span(events=[_event("gen_ai.user.message", {"role": "user"})])
    assert gen_ai_message_event_attribute_types(span, _registry()) == []


def test_choice_event_with_valid_system_passes() -> None:
    span = _span(events=[_event("gen_ai.choice", {"gen_ai.system": "openai"})])
    assert gen_ai_choice_event_attribute_types(span, _registry()) == []


def test_choice_event_with_non_string_system_is_flagged() -> None:
    # arrange
    span = _span(events=[_event("gen_ai.choice", {"gen_ai.system": 42})])
    # act
    findings = gen_ai_choice_event_attribute_types(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.system.type"
    assert "gen_ai.choice" in findings[0].message


def test_choice_event_with_wrong_typed_finish_reasons_is_flagged() -> None:
    # arrange
    span = _span(events=[_event("gen_ai.choice", {"gen_ai.response.finish_reasons": "stop"})])
    # act
    findings = gen_ai_choice_event_attribute_types(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.response.finish_reasons.type"


def test_message_event_is_not_scanned_by_choice_rule() -> None:
    span = _span(events=[_event("gen_ai.user.message", {"gen_ai.system": 123})])
    assert gen_ai_choice_event_attribute_types(span, _registry()) == []


def test_span_with_no_events_is_not_flagged_by_choice_rule() -> None:
    span = _span({"gen_ai.system": "openai"})
    assert gen_ai_choice_event_attribute_types(span, _registry()) == []


def test_choice_event_with_unknown_attribute_is_not_flagged() -> None:
    span = _span(events=[_event("gen_ai.choice", {"index": 0})])
    assert gen_ai_choice_event_attribute_types(span, _registry()) == []


def test_token_usage_histogram_with_token_unit_passes() -> None:
    # arrange
    m = Metric(
        name="gen_ai.client.token.usage",
        instrument=InstrumentType.HISTOGRAM,
        unit="{token}",
    )
    # act / assert
    assert gen_ai_client_token_usage_metric(m, _registry()) == []


def test_token_usage_wrong_instrument_is_flagged() -> None:
    # arrange
    m = Metric(
        name="gen_ai.client.token.usage",
        instrument=InstrumentType.COUNTER,
        unit="{token}",
    )
    # act
    findings = gen_ai_client_token_usage_metric(m, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.client.token.usage.instrument"
    assert "counter" in findings[0].message


def test_token_usage_wrong_unit_is_flagged() -> None:
    # arrange
    m = Metric(
        name="gen_ai.client.token.usage",
        instrument=InstrumentType.HISTOGRAM,
        unit="tokens",
    )
    # act
    findings = gen_ai_client_token_usage_metric(m, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.client.token.usage.unit"


def test_token_usage_both_wrong_produces_two_findings() -> None:
    # arrange
    m = Metric(name="gen_ai.client.token.usage", instrument=InstrumentType.COUNTER, unit="")
    # act
    findings = gen_ai_client_token_usage_metric(m, _registry())
    # assert
    assert {f.rule for f in findings} == {
        "gen_ai.client.token.usage.instrument",
        "gen_ai.client.token.usage.unit",
    }


def test_token_usage_rule_ignores_other_metrics() -> None:
    m = Metric(name="some.other.metric", instrument=InstrumentType.COUNTER)
    assert gen_ai_client_token_usage_metric(m, _registry()) == []


def test_operation_duration_histogram_with_second_unit_passes() -> None:
    # arrange
    m = Metric(
        name="gen_ai.client.operation.duration",
        instrument=InstrumentType.HISTOGRAM,
        unit="s",
    )
    # act / assert
    assert gen_ai_client_operation_duration_metric(m, _registry()) == []


def test_operation_duration_wrong_instrument_is_flagged() -> None:
    # arrange
    m = Metric(
        name="gen_ai.client.operation.duration",
        instrument=InstrumentType.GAUGE,
        unit="s",
    )
    # act
    findings = gen_ai_client_operation_duration_metric(m, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.client.operation.duration.instrument"
    assert "gauge" in findings[0].message


def test_operation_duration_wrong_unit_is_flagged() -> None:
    # arrange
    m = Metric(
        name="gen_ai.client.operation.duration",
        instrument=InstrumentType.HISTOGRAM,
        unit="ms",
    )
    # act
    findings = gen_ai_client_operation_duration_metric(m, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.client.operation.duration.unit"


def test_operation_duration_both_wrong_produces_two_findings() -> None:
    # arrange
    m = Metric(
        name="gen_ai.client.operation.duration",
        instrument=InstrumentType.COUNTER,
    )
    # act
    findings = gen_ai_client_operation_duration_metric(m, _registry())
    # assert
    assert {f.rule for f in findings} == {
        "gen_ai.client.operation.duration.instrument",
        "gen_ai.client.operation.duration.unit",
    }


def test_operation_duration_rule_ignores_other_metrics() -> None:
    m = Metric(name="gen_ai.client.token.usage", instrument=InstrumentType.HISTOGRAM)
    assert gen_ai_client_operation_duration_metric(m, _registry()) == []


def test_no_deprecated_names_passes() -> None:
    span = _span({"gen_ai.system": "openai", "gen_ai.request.model": "gpt-4"})
    assert gen_ai_deprecated_attribute_name(span, _registry()) == []


def test_gen_ai_prompt_is_flagged_with_event_replacement() -> None:
    # arrange
    span = _span({"gen_ai.prompt": "say hi"})
    # act
    findings = gen_ai_deprecated_attribute_name(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.deprecated.gen_ai.prompt"
    assert findings[0].target == "chat"
    assert "gen_ai.user.message" in findings[0].message


def test_llm_carryover_names_each_get_a_finding() -> None:
    # arrange
    span = _span(
        {
            "llm.model_name": "gpt-4",
            "llm.temperature": 0.7,
            "llm.usage.prompt_tokens": 12,
        }
    )
    # act
    findings = gen_ai_deprecated_attribute_name(span, _registry())
    # assert
    rules = {f.rule for f in findings}
    assert rules == {
        "gen_ai.deprecated.llm.model_name",
        "gen_ai.deprecated.llm.temperature",
        "gen_ai.deprecated.llm.usage.prompt_tokens",
    }
    by_rule = {f.rule: f.message for f in findings}
    assert "gen_ai.request.model" in by_rule["gen_ai.deprecated.llm.model_name"]
    assert "gen_ai.request.temperature" in by_rule["gen_ai.deprecated.llm.temperature"]
    assert "gen_ai.usage.input_tokens" in by_rule["gen_ai.deprecated.llm.usage.prompt_tokens"]


def test_current_and_deprecated_mixed_only_flags_deprecated() -> None:
    # arrange
    span = _span({"gen_ai.request.model": "gpt-4", "gen_ai.completion": "hi there"})
    # act
    findings = gen_ai_deprecated_attribute_name(span, _registry())
    # assert
    assert len(findings) == 1
    assert findings[0].rule == "gen_ai.deprecated.gen_ai.completion"
    assert "gen_ai.choice" in findings[0].message
