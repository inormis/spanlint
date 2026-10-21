from __future__ import annotations

from ..model import Span

_SCOPES = frozenset(
    {
        "openai",
        "opentelemetry.instrumentation.openai",
        "opentelemetry.instrumentation.openai_v2",
        "opentelemetry.instrumentation.openai.v1",
    }
)


def is_openai_span(span: Span) -> bool:
    if span.instrumentation_scope in _SCOPES:
        return True
    attrs = span.attributes
    return "openai" in (attrs.get("gen_ai.system"), attrs.get("gen_ai.provider.name"))
