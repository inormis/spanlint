from __future__ import annotations

from ..model import Span

_SCOPES = frozenset(
    {
        "opentelemetry.instrumentation.langchain",
        "openinference.instrumentation.langchain",
    }
)

_PROVIDERS = frozenset({"langchain", "langgraph"})


def is_langchain_span(span: Span) -> bool:
    if span.instrumentation_scope in _SCOPES:
        return True
    return span.attributes.get("gen_ai.provider.name") in _PROVIDERS
