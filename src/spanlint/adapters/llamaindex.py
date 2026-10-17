from __future__ import annotations

from ..model import Span

_SCOPES = frozenset(
    {
        "opentelemetry.instrumentation.llamaindex",
        "openinference.instrumentation.llama_index",
        "llamaindex.opentelemetry.tracer",
    }
)


def is_llamaindex_span(span: Span) -> bool:
    return span.instrumentation_scope in _SCOPES
