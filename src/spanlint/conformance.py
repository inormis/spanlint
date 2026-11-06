from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from spanlint.adapters.langchain import is_langchain_span
from spanlint.adapters.langfuse import is_langfuse_span
from spanlint.adapters.litellm import is_litellm_span
from spanlint.adapters.llamaindex import is_llamaindex_span
from spanlint.adapters.meai import is_meai_span
from spanlint.adapters.openai import is_openai_span
from spanlint.adapters.semantic_kernel import is_semantic_kernel_span
from spanlint.adapters.traceloop import is_traceloop_span
from spanlint.adapters.vercel_ai import is_vercel_ai_span
from spanlint.model import Span
from spanlint.otlp import parse_otlp_json_file
from spanlint.registry import Registry
from spanlint.rules import DEFAULT_SPAN_RULES, gen_ai_attributes_missing
from spanlint.validate import Rule, validate

Adapter = Callable[[Span], bool]

# Keyed by the fixture directory each framework's captures live in.
ADAPTERS: dict[str, Adapter] = {
    "langchain": is_langchain_span,
    "langfuse": is_langfuse_span,
    "litellm": is_litellm_span,
    "llamaindex": is_llamaindex_span,
    "meai": is_meai_span,
    "openai": is_openai_span,
    "semantic_kernel": is_semantic_kernel_span,
    "traceloop": is_traceloop_span,
    "vercel_ai": is_vercel_ai_span,
}

MATRIX_RULES: tuple[Rule, ...] = (*DEFAULT_SPAN_RULES, gen_ai_attributes_missing)


def run_matrix(fixtures: Path, registry: Registry) -> dict[str, dict[str, int]]:
    """Run each framework's fixtures through its adapter and count findings per rule."""
    matrix: dict[str, dict[str, int]] = {}
    for framework, adapter in sorted(ADAPTERS.items()):
        files = sorted((fixtures / framework).glob("*.json"))
        if not files:
            continue
        counts: dict[str, int] = {}
        for file in files:
            spans = [span for span in parse_otlp_json_file(file) if adapter(span)]
            for finding in validate(spans, MATRIX_RULES, registry):
                counts[finding.rule] = counts.get(finding.rule, 0) + 1
        matrix[framework] = dict(sorted(counts.items()))
    return matrix
