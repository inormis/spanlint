"""Runs one OpenAI chat completion through Langfuse and prints the spans as OTLP JSON.

Langfuse's OpenAI wrapper makes a generation span for the call and the
@observe decorator around it adds the parent. The client is handed an
in-memory exporter in place of the one that would talk to Langfuse, so the
project keys are placeholders and nothing leaves the process except the
OpenAI request. Needs OPENAI_API_KEY.
"""

from __future__ import annotations

import base64
import json
import sys
from typing import Any

from google.protobuf.json_format import MessageToDict
from langfuse import Langfuse, observe
from langfuse.openai import openai
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
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


@observe(name="greet")
def _greet() -> str:
    response = openai.OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hi in one word."}],
        temperature=0,
        max_tokens=16,
    )
    return response.choices[0].message.content or ""


def main() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "spanlint-fixtures"}))
    langfuse = Langfuse(
        public_key="pk-lf-fixtures",
        secret_key="placeholder",
        tracer_provider=provider,
        span_exporter=exporter,
    )
    _greet()
    langfuse.flush()

    payload = MessageToDict(encode_spans(exporter.get_finished_spans()))
    _hex_ids(payload)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
