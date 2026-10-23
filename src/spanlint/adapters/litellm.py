from __future__ import annotations

from ..model import Span

_SCOPES = frozenset(
    {
        "litellm",
        "opentelemetry.instrumentation.litellm",
        "openinference.instrumentation.litellm",
    }
)


def is_litellm_span(span: Span) -> bool:
    return span.instrumentation_scope in _SCOPES
