from __future__ import annotations

from pathlib import Path

import pytest

from spanlint.adapters.semantic_kernel import is_semantic_kernel_span
from spanlint.model import Span, SpanKind
from spanlint.otlp import parse_otlp_json_file

FIXTURE = Path(__file__).parent / "fixtures" / "semantic_kernel" / "invoke_prompt.json"


def _bare(**kw: object) -> Span:
    defaults: dict[str, object] = {
        "name": "s",
        "kind": SpanKind.INTERNAL,
        "start_time_unix_nano": 0,
        "end_time_unix_nano": 1,
    }
    defaults.update(kw)
    return Span(**defaults)  # type: ignore[arg-type]


def test_identifies_every_span_in_fixture() -> None:
    spans = parse_otlp_json_file(FIXTURE)
    assert len(spans) == 2
    assert all(is_semantic_kernel_span(span) for span in spans)


@pytest.mark.parametrize(
    "scope",
    [
        "semantic_kernel.utils.telemetry.model_diagnostics.decorators",
        "semantic_kernel.functions.kernel_function",
        "semantic_kernel.connectors.ai.chat_completion_client_base",
        "semantic_kernel.utils.telemetry.agent_diagnostics.decorators",
    ],
)
def test_identifies_by_module_scope_name(scope: str) -> None:
    assert is_semantic_kernel_span(_bare(instrumentation_scope=scope))


def test_rejects_scope_that_only_starts_with_the_word() -> None:
    assert not is_semantic_kernel_span(
        _bare(instrumentation_scope="semantic_kernel_extras.tracing")
    )


def test_rejects_openai_span_with_matching_attributes() -> None:
    span = _bare(
        instrumentation_scope="opentelemetry.instrumentation.openai_v2",
        attributes={"gen_ai.system": "openai", "gen_ai.operation.name": "chat"},
    )
    assert not is_semantic_kernel_span(span)


def test_rejects_span_with_no_signal() -> None:
    assert not is_semantic_kernel_span(_bare())
