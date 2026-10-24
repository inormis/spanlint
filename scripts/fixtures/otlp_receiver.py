"""Receives one OTLP/HTTP trace export on localhost and prints it as OTLP JSON.

For capture programs written against OpenTelemetry SDKs that only speak
protobuf. Listens on 127.0.0.1 at the port given as the first argument (4318
by default), accepts POSTs to /v1/traces until the sender has gone quiet,
then writes the decoded spans to stdout in the same shape as the Python
captures.
"""

from __future__ import annotations

import base64
import json
import sys
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from typing import Any

from google.protobuf.json_format import MessageToDict
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
    ExportTraceServiceRequest,
    ExportTraceServiceResponse,
)

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


class _Server(TCPServer):
    # Not HTTPServer: its bind step reverse-resolves the address, which can
    # stall for longer than the exporter is willing to wait.
    allow_reuse_address = True

    def __init__(self, port: int) -> None:
        super().__init__(("127.0.0.1", port), _Handler)
        self.received = ExportTraceServiceRequest()
        self.posts = 0


class _Handler(BaseHTTPRequestHandler):
    server: _Server

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"]))
        request = ExportTraceServiceRequest()
        request.ParseFromString(body)
        self.server.received.resource_spans.extend(request.resource_spans)
        self.server.posts += 1
        self.send_response(200)
        self.send_header("Content-Type", "application/x-protobuf")
        self.end_headers()
        self.wfile.write(ExportTraceServiceResponse().SerializeToString())

    def log_message(self, format: str, *args: Any) -> None:
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4318
    server = _Server(port)
    server.handle_request()
    # A batch processor may split one shutdown flush over several posts, so
    # keep going until a second passes with nothing new.
    server.timeout = 1
    seen = server.posts
    while True:
        server.handle_request()
        if server.posts == seen:
            break
        seen = server.posts

    payload = MessageToDict(server.received)
    _hex_ids(payload)
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
