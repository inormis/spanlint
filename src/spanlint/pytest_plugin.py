"""Pytest plugin exposing fixtures for capturing OpenTelemetry spans during tests."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any

import pytest

from spanlint.model import AttributeValue, Event, Span, SpanKind, Status, StatusCode

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import ReadableSpan
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
        InMemorySpanExporter,
    )


class CapturedSpans:
    def __init__(self, exporter: InMemorySpanExporter) -> None:
        self._exporter = exporter

    @property
    def spans(self) -> list[Span]:
        return [_convert(s) for s in self._exporter.get_finished_spans()]

    def clear(self) -> None:
        self._exporter.clear()


@pytest.fixture
def spanlint_spans() -> Iterator[CapturedSpans]:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
            InMemorySpanExporter,
        )
    except ImportError as exc:
        raise pytest.UsageError(
            "spanlint_spans requires opentelemetry-sdk; install spanlint[pytest]"
        ) from exc

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    previous = trace._TRACER_PROVIDER
    trace._TRACER_PROVIDER = provider
    try:
        yield CapturedSpans(exporter)
    finally:
        trace._TRACER_PROVIDER = previous
        provider.shutdown()


_STATUS_MAP = {
    "UNSET": StatusCode.UNSET,
    "OK": StatusCode.OK,
    "ERROR": StatusCode.ERROR,
}


def _convert(readable: ReadableSpan) -> Span:
    kind = SpanKind[readable.kind.name]
    status = Status(
        code=_STATUS_MAP[readable.status.status_code.name],
        description=readable.status.description or "",
    )
    scope = readable.instrumentation_scope.name if readable.instrumentation_scope else None
    return Span(
        name=readable.name,
        kind=kind,
        start_time_unix_nano=readable.start_time or 0,
        end_time_unix_nano=readable.end_time or 0,
        attributes=_attrs(readable.attributes),
        events=[
            Event(
                name=ev.name,
                timestamp_unix_nano=ev.timestamp,
                attributes=_attrs(ev.attributes),
            )
            for ev in readable.events
        ],
        status=status,
        instrumentation_scope=scope,
    )


def _attrs(raw: Mapping[str, Any] | None) -> dict[str, AttributeValue]:
    if not raw:
        return {}
    out: dict[str, AttributeValue] = {}
    for k, v in raw.items():
        out[k] = list(v) if isinstance(v, tuple) else v
    return out
