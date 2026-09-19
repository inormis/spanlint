from __future__ import annotations

from spanlint.model import AttributeValue, Span
from spanlint.registry import Registry
from spanlint.validate import Finding


def gen_ai_system_required(span: Span, registry: Registry) -> list[Finding]:
    if not _has_gen_ai_attributes(span):
        return []
    if "gen_ai.system" in span.attributes:
        return []
    return [
        Finding(
            rule="gen_ai.system.required",
            span=span.name,
            message="gen_ai.system is required on GenAI spans",
        )
    ]


def gen_ai_operation_name_enum(span: Span, registry: Registry) -> list[Finding]:
    value = span.attributes.get("gen_ai.operation.name")
    if not isinstance(value, str):
        return []
    attr = registry.attribute("gen_ai.operation.name")
    if attr is None or attr.type != "enum" or value in attr.enum_members:
        return []
    return [
        Finding(
            rule="gen_ai.operation.name.enum",
            span=span.name,
            message=f"gen_ai.operation.name={value!r} is not a known operation",
        )
    ]


def gen_ai_request_model_type(span: Span, registry: Registry) -> list[Finding]:
    return _check_attribute_type(span, registry, "gen_ai.request.model")


def gen_ai_response_model_type(span: Span, registry: Registry) -> list[Finding]:
    return _check_attribute_type(span, registry, "gen_ai.response.model")


def gen_ai_request_temperature_type(span: Span, registry: Registry) -> list[Finding]:
    return _check_attribute_type(span, registry, "gen_ai.request.temperature")


def gen_ai_request_top_p_type(span: Span, registry: Registry) -> list[Finding]:
    return _check_attribute_type(span, registry, "gen_ai.request.top_p")


def gen_ai_request_max_tokens_type(span: Span, registry: Registry) -> list[Finding]:
    return _check_attribute_type(span, registry, "gen_ai.request.max_tokens")


def gen_ai_response_id_type(span: Span, registry: Registry) -> list[Finding]:
    return _check_attribute_type(span, registry, "gen_ai.response.id")


def gen_ai_response_finish_reasons_type(span: Span, registry: Registry) -> list[Finding]:
    return _check_attribute_type(span, registry, "gen_ai.response.finish_reasons")


def _check_attribute_type(span: Span, registry: Registry, name: str) -> list[Finding]:
    if name not in span.attributes:
        return []
    value = span.attributes[name]
    attr = registry.attribute(name)
    if attr is None or _matches_type(value, attr.type):
        return []
    return [
        Finding(
            rule=f"{name}.type",
            span=span.name,
            message=f"{name} must be a {attr.type}",
        )
    ]


def _matches_type(value: AttributeValue, type_str: str) -> bool:
    if type_str == "string":
        return isinstance(value, str)
    if type_str == "double":
        return isinstance(value, float)
    if type_str == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_str == "string[]":
        return isinstance(value, list) and all(isinstance(v, str) for v in value)
    return True


def _has_gen_ai_attributes(span: Span) -> bool:
    return any(k.startswith("gen_ai.") for k in span.attributes)
