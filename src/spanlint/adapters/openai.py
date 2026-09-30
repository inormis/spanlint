from __future__ import annotations

from ..model import Span

_SCOPES = frozenset(
    {
        "openai",
        "opentelemetry.instrumentation.openai",
        "opentelemetry.instrumentation.openai_v2",
    }
)


def is_openai_span(span: Span) -> bool:
    if span.instrumentation_scope in _SCOPES:
        return True
    return span.attributes.get("gen_ai.system") == "openai"
