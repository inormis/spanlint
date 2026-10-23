"""Runs one Semantic Kernel prompt against OpenAI and prints the spans as OTLP JSON.

Semantic Kernel reads its diagnostics flag when it is imported, so it is set
here before anything from it is imported. The separate sensitive flag writes
message content to Python logging rather than to span events, so it adds
nothing to this file and stays off. Needs OPENAI_API_KEY.
"""

from __future__ import annotations

import asyncio
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

os.environ.setdefault("SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS", "true")

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


async def _run() -> None:
    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import (
        OpenAIChatCompletion,
        OpenAIChatPromptExecutionSettings,
    )
    from semantic_kernel.functions import KernelArguments

    kernel = Kernel()
    kernel.add_service(OpenAIChatCompletion(ai_model_id="gpt-4o-mini"))
    settings = OpenAIChatPromptExecutionSettings(temperature=0, max_tokens=16)
    await kernel.invoke_prompt(
        "Say hi in one word.",
        function_name="greet",
        plugin_name="fixtures",
        arguments=KernelArguments(settings=settings),
    )


def main() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "spanlint-fixtures"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    asyncio.run(_run())

    payload = MessageToDict(encode_spans(exporter.get_finished_spans()))
    _hex_ids(payload)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
