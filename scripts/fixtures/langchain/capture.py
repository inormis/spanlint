"""Runs a one-step LangChain chain under Traceloop's instrumentation and prints OTLP JSON.

Needs OPENAI_API_KEY. The output is what tests/fixtures/langchain/chain.json was made from.
"""

from __future__ import annotations

import base64
import json
import sys
from typing import Any

from google.protobuf.json_format import MessageToDict
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
from opentelemetry.instrumentation.langchain import LangchainInstrumentor
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


def main() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "spanlint-fixtures"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    LangchainInstrumentor().instrument()

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI

    prompt = ChatPromptTemplate.from_messages([("user", "{question}")])
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=16)
    (prompt | model).invoke({"question": "Say hi in one word."})

    payload = MessageToDict(encode_spans(exporter.get_finished_spans()))
    _hex_ids(payload)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
