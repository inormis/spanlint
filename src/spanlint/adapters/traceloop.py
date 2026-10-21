from __future__ import annotations

from ..model import Span

# The SDK's own workflow/task/agent/tool spans. Spans from Traceloop's
# per-framework instrumentations belong to the framework adapters.
_SCOPES = frozenset({"traceloop.tracer"})


def is_traceloop_span(span: Span) -> bool:
    return span.instrumentation_scope in _SCOPES
