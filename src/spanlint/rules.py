from __future__ import annotations

from spanlint.model import Span
from spanlint.registry import Registry
from spanlint.validate import Finding


def gen_ai_system_required(span: Span, registry: Registry) -> list[Finding]:
    if not _has_gen_ai_attributes(span):
        return []
    if "gen_ai.system" in span.attributes:
        return []
    return [
        Finding(
            rule="gen_ai.system.required",
            span=span.name,
            message="gen_ai.system is required on GenAI spans",
        )
    ]


def _has_gen_ai_attributes(span: Span) -> bool:
    return any(k.startswith("gen_ai.") for k in span.attributes)
