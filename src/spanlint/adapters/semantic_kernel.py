from __future__ import annotations

from ..model import Span

# Semantic Kernel names every tracer after the module that owns it, so the
# scopes are a family rather than a fixed list.
_SCOPE_PREFIX = "semantic_kernel."


def is_semantic_kernel_span(span: Span) -> bool:
    scope = span.instrumentation_scope or ""
    return scope.startswith(_SCOPE_PREFIX)
