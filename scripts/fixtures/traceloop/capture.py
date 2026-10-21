"""Runs a Traceloop SDK workflow around one OpenAI call and prints the spans as OTLP JSON.

Only the OpenAI instrument is switched on, so the output holds the SDK's own
workflow and task spans (scope traceloop.tracer) next to the openai.chat span
from Traceloop's OpenAI instrumentation. Needs OPENAI_API_KEY.
"""

from __future__ import annotations

import base64
import contextlib
import json
import sys
from typing import Any

from google.protobuf.json_format import MessageToDict
from opentelemetry.exporter.otlp.proto.common.trace_encoder import encode_spans
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from traceloop.sdk import Instruments, Traceloop
from traceloop.sdk.decorators import task, workflow

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


@task(name="ask")
def ask(question: str) -> str:
    from openai import OpenAI

    response = OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
        temperature=0,
        max_tokens=16,
    )
    return response.choices[0].message.content or ""


@workflow(name="greet")
def greet() -> str:
    return ask("Say hi in one word.")


def main() -> None:
    exporter = InMemorySpanExporter()
    # Traceloop.init prints a banner to stdout, which is where the JSON goes
    with contextlib.redirect_stdout(sys.stderr):
        Traceloop.init(
            app_name="spanlint-fixtures",
            exporter=exporter,
            disable_batch=True,
            telemetry_enabled=False,
            instruments={Instruments.OPENAI},
        )
    greet()

    payload = MessageToDict(encode_spans(exporter.get_finished_spans()))
    _hex_ids(payload)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
