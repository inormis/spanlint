from __future__ import annotations

from ..model import Span

# @ai-sdk/otel names its tracer gen_ai, or ai for the pre-7 span shape it
# still offers as LegacyOpenTelemetry. Either can be given another tracer;
# the legacy spans still carry ai.operationId then, the semconv ones carry
# nothing of the SDK's own.
_SCOPES = frozenset({"gen_ai", "ai"})


def is_vercel_ai_span(span: Span) -> bool:
    if span.instrumentation_scope in _SCOPES:
        return True
    return "ai.operationId" in span.attributes
