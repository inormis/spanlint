from __future__ import annotations

from ..model import Span

# Langfuse's own processor recognises its spans the same way, by this one
# tracer name. The langfuse.* attributes are no use as a fallback: the
# processor also copies propagated ones onto third-party spans.
_SCOPE = "langfuse-sdk"


def is_langfuse_span(span: Span) -> bool:
    return span.instrumentation_scope == _SCOPE
