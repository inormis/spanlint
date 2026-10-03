from __future__ import annotations

import pytest
from opentelemetry import trace
from opentelemetry.trace import SpanKind as OTelSpanKind
from opentelemetry.trace import StatusCode as OTelStatusCode

from spanlint.model import SpanKind, StatusCode
from spanlint.pytest_plugin import CapturedSpans

pytest_plugins = ["pytester"]


def test_captures_a_simple_span(spanlint_spans: CapturedSpans) -> None:
    tracer = trace.get_tracer("demo")
    with tracer.start_as_current_span("op") as span:
        span.set_attribute("k", "v")

    assert len(spanlint_spans.spans) == 1
    captured = spanlint_spans.spans[0]
    assert captured.name == "op"
    assert captured.attributes["k"] == "v"
    assert captured.instrumentation_scope == "demo"


def test_converts_kind_status_and_events(spanlint_spans: CapturedSpans) -> None:
    tracer = trace.get_tracer("demo")
    with tracer.start_as_current_span("op", kind=OTelSpanKind.CLIENT) as span:
        span.set_attribute("n", 1)
        span.set_attribute("items", ("a", "b"))
        span.add_event("thing", {"x": 1})
        span.set_status(OTelStatusCode.ERROR, "something went wrong")

    captured = spanlint_spans.spans[0]
    assert captured.kind == SpanKind.CLIENT
    assert captured.status.code == StatusCode.ERROR
    assert captured.status.description == "something went wrong"
    assert captured.attributes["n"] == 1
    assert captured.attributes["items"] == ["a", "b"]
    assert len(captured.events) == 1
    assert captured.events[0].name == "thing"
    assert captured.events[0].attributes == {"x": 1}


def test_each_test_sees_only_its_own_spans(spanlint_spans: CapturedSpans) -> None:
    tracer = trace.get_tracer("demo")
    with tracer.start_as_current_span("only-mine"):
        pass
    names = [s.name for s in spanlint_spans.spans]
    assert names == ["only-mine"]


def test_clear_drops_already_captured_spans(spanlint_spans: CapturedSpans) -> None:
    tracer = trace.get_tracer("demo")
    with tracer.start_as_current_span("first"):
        pass
    spanlint_spans.clear()
    with tracer.start_as_current_span("second"):
        pass
    assert [s.name for s in spanlint_spans.spans] == ["second"]


def test_restores_global_provider_after_fixture(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        """
        from opentelemetry import trace

        def test_a(spanlint_spans):
            assert trace._TRACER_PROVIDER is not None

        def test_b_sees_no_captured_spans():
            # the fixture tore itself down; the provider that recorded
            # spans in test_a is gone
            tracer = trace.get_tracer('x')
            with tracer.start_as_current_span('untracked'):
                pass
        """
    )
    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=2)
