from __future__ import annotations

from ..model import Span

# The library's default ActivitySource. An application can hand UseOpenTelemetry
# its own name, and those spans carry nothing else that points back here.
_SCOPE = "Experimental.Microsoft.Extensions.AI"


def is_meai_span(span: Span) -> bool:
    return span.instrumentation_scope == _SCOPE
