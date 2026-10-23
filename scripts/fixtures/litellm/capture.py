"""Runs one LiteLLM completion and prints the spans as OTLP JSON.

The first argument picks the instrumentation: `native` for LiteLLM's own
OpenTelemetry callback, `traceloop` for Traceloop's LiteLLM instrumentation.
Needs OPENAI_API_KEY. The files under tests/fixtures/litellm/ were made from
one run of each.
"""

from __future__ import annotations

import base64
import contextlib
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
_ACCOUNT_HEADERS = ("openai-organization", "openai-project", "set-cookie")


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


def _scrub_account_headers(payload: Any) -> None:
    # LiteLLM copies the provider's raw response headers into hidden_params, and
    # OpenAI's carry the organisation and project ids of the account that made
    # the call plus a Cloudflare cookie. None of that bears on conformance.
    for resource in payload["resourceSpans"]:
        for scope in resource["scopeSpans"]:
            for span in scope["spans"]:
                for attr in span.get("attributes", []):
                    if attr["key"] != "hidden_params":
                        continue
                    hidden = json.loads(attr["value"]["stringValue"])
                    headers = hidden.get("additional_headers") or {}
                    for key in headers:
                        if key.endswith(_ACCOUNT_HEADERS):
                            headers[key] = "redacted"
                    attr["value"]["stringValue"] = json.dumps(hidden)


def _resource() -> Resource:
    return Resource.create({"service.name": "spanlint-fixtures"})


def _native(exporter: InMemorySpanExporter) -> None:
    import litellm
    from litellm.integrations.opentelemetry import OpenTelemetry, OpenTelemetryConfig

    config = OpenTelemetryConfig(exporter=exporter, service_name="spanlint-fixtures")
    litellm.callbacks = [OpenTelemetry(config=config)]


def _traceloop(exporter: InMemorySpanExporter) -> None:
    from opentelemetry.instrumentation.litellm import LiteLLMInstrumentor

    provider = TracerProvider(resource=_resource())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    LiteLLMInstrumentor().instrument()


def _run() -> None:
    import litellm

    litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say hi in one word."}],
        temperature=0,
        max_tokens=16,
    )
    # LiteLLM fires success callbacks from a worker thread after completion()
    # has returned, so the native span is not finished until that thread is.
    from litellm.litellm_core_utils.thread_pool_executor import executor

    executor.shutdown(wait=True)


def main(mode: str) -> None:
    exporter = InMemorySpanExporter()
    # LiteLLM writes its own notices to stdout, which is where the JSON goes
    with contextlib.redirect_stdout(sys.stderr):
        {"native": _native, "traceloop": _traceloop}[mode](exporter)
        _run()

    payload = MessageToDict(encode_spans(exporter.get_finished_spans()))
    _hex_ids(payload)
    _scrub_account_headers(payload)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("native", "traceloop"):
        sys.exit("usage: capture.py native|traceloop")
    main(sys.argv[1])
