"""Runs a one-turn LlamaIndex chat engine and prints the spans as OTLP JSON.

The first argument picks the instrumentation: `native` for LlamaIndex's own OTel
bridge (llama-index-observability-otel), `traceloop` for Traceloop's LlamaIndex
and OpenAI instrumentations. Needs OPENAI_API_KEY. The files under
tests/fixtures/llamaindex/ were made from one run of each.
"""

from __future__ import annotations

import base64
import json
import sys
from typing import Any

from google.protobuf.json_format import MessageToDict
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

_ID_KEYS = ("traceId", "spanId", "parentSpanId")


def _hex_ids(node: Any) -> None:
    # protobuf's JSON mapping base64-encodes bytes fields; OTLP/JSON wants hex
    if isinstance(node, dict):
        for key, value in node.items():
            if key in _ID_KEYS and isinstance(value, str):
                node[key] = base64.b64decode(value).hex()
            else:
                _hex_ids(value)
    elif isinstance(node, list):
        for item in node:
            _hex_ids(item)


def _resource() -> Resource:
    return Resource.create({"service.name": "spanlint-fixtures"})


def _native(exporter: InMemorySpanExporter) -> None:
    from llama_index.observability.otel import LlamaIndexOpenTelemetry

    LlamaIndexOpenTelemetry(
        span_exporter=exporter,
        span_processor="simple",
        service_name_or_resource=_resource(),
    ).start_registering()


def _traceloop(exporter: InMemorySpanExporter) -> None:
    from opentelemetry.instrumentation.llamaindex import LlamaIndexInstrumentor
    from opentelemetry.instrumentation.openai import OpenAIInstrumentor

    provider = TracerProvider(resource=_resource())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    LlamaIndexInstrumentor().instrument()
    # Traceloop leaves the OpenAI call to its OpenAI instrumentation instead of
    # making a LlamaIndex span for it, so without this the model call is invisible.
    OpenAIInstrumentor().instrument()


def main(mode: str) -> None:
    exporter = InMemorySpanExporter()
    {"native": _native, "traceloop": _traceloop}[mode](exporter)

    from llama_index.core.chat_engine import SimpleChatEngine
    from llama_index.llms.openai import OpenAI

    llm = OpenAI(model="gpt-4o-mini", temperature=0, max_tokens=16)
    SimpleChatEngine.from_defaults(llm=llm).chat("Say hi in one word.")

    payload = MessageToDict(encode_spans(exporter.get_finished_spans()))
    _hex_ids(payload)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("native", "traceloop"):
        sys.exit("usage: capture.py native|traceloop")
    main(sys.argv[1])
