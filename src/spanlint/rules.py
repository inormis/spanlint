from __future__ import annotations

from spanlint.model import Span
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


def _has_gen_ai_attributes(span: Span) -> bool:
    return any(k.startswith("gen_ai.") for k in span.attributes)
