"""Runs one chat completion through opentelemetry-instrumentation-openai-v2
and prints the spans as OTLP JSON.

The first argument picks the attribute set: `default` for what the
instrumentation emits out of the box, `latest` for the current conventions,
which it only emits with OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental.
Needs OPENAI_API_KEY. The files under tests/fixtures/openai/ were made from
one run of each.
"""

from __future__ import annotations

import base64
import json
import os
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


def main(mode: str) -> None:
    if mode == "latest":
        os.environ["OTEL_SEMCONV_STABILITY_OPT_IN"] = "gen_ai_latest_experimental"
    os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "SPAN_ONLY"
    # the instrumentation reads both variables when it is set up, so import late
    from openai import OpenAI
    from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "spanlint-fixtures"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    OpenAIInstrumentor().instrument()

    try:
        OpenAI().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hi in one word."}],
            temperature=0,
            max_tokens=16,
        )
    finally:
        provider.shutdown()

    payload = MessageToDict(encode_spans(exporter.get_finished_spans()))
    _hex_ids(payload)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("default", "latest"):
        sys.exit("usage: capture.py default|latest")
    main(sys.argv[1])
