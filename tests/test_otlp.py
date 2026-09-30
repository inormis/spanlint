from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from spanlint.model import SpanKind, StatusCode
from spanlint.otlp import parse_otlp_json, parse_otlp_json_file


def _wrap(spans: list[dict[str, Any]]) -> dict[str, Any]:
    return {"resourceSpans": [{"scopeSpans": [{"spans": spans}]}]}


def test_empty_export_yields_no_spans() -> None:
    assert parse_otlp_json({}) == []
    assert parse_otlp_json({"resourceSpans": []}) == []


def test_minimal_span() -> None:
    spans = parse_otlp_json(
        _wrap(
            [
                {
                    "name": "chat",
                    "kind": 3,
                    "startTimeUnixNano": "1700000000000000000",
                    "endTimeUnixNano": "1700000000100000000",
                }
            ]
        )
    )
    assert len(spans) == 1
    s = spans[0]
    assert s.name == "chat"
    assert s.kind is SpanKind.CLIENT
    assert s.start_time_unix_nano == 1_700_000_000_000_000_000
    assert s.end_time_unix_nano == 1_700_000_000_100_000_000
    assert s.attributes == {}
    assert s.events == []
    assert s.status.code is StatusCode.UNSET
    assert s.instrumentation_scope is None


def test_instrumentation_scope_from_scope_name() -> None:
    data = {
        "resourceSpans": [
            {
                "scopeSpans": [
                    {
                        "scope": {"name": "openai", "version": "1.2.3"},
                        "spans": [
                            {
                                "name": "chat",
                                "kind": 3,
                                "startTimeUnixNano": "0",
                                "endTimeUnixNano": "1",
                            }
                        ],
                    }
                ]
            }
        ]
    }
    spans = parse_otlp_json(data)
    assert spans[0].instrumentation_scope == "openai"


def test_span_kind_mapping() -> None:
    for k, expected in [
        (0, SpanKind.INTERNAL),
        (1, SpanKind.INTERNAL),
        (2, SpanKind.SERVER),
        (3, SpanKind.CLIENT),
        (4, SpanKind.PRODUCER),
        (5, SpanKind.CONSUMER),
        ("SPAN_KIND_SERVER", SpanKind.SERVER),
    ]:
        spans = parse_otlp_json(
            _wrap(
                [
                    {
                        "name": "s",
                        "kind": k,
                        "startTimeUnixNano": "0",
                        "endTimeUnixNano": "1",
                    }
                ]
            )
        )
        assert spans[0].kind is expected


def test_status_ok_with_message() -> None:
    spans = parse_otlp_json(
        _wrap(
            [
                {
                    "name": "s",
                    "kind": 1,
                    "startTimeUnixNano": "0",
                    "endTimeUnixNano": "1",
                    "status": {"code": 2, "message": "boom"},
                }
            ]
        )
    )
    assert spans[0].status.code is StatusCode.ERROR
    assert spans[0].status.description == "boom"


def test_attribute_value_types() -> None:
    spans = parse_otlp_json(
        _wrap(
            [
                {
                    "name": "s",
                    "kind": 3,
                    "startTimeUnixNano": "0",
                    "endTimeUnixNano": "1",
                    "attributes": [
                        {"key": "gen_ai.system", "value": {"stringValue": "openai"}},
                        {"key": "gen_ai.request.temperature", "value": {"doubleValue": 0.7}},
                        {"key": "gen_ai.request.max_tokens", "value": {"intValue": "128"}},
                        {"key": "stream", "value": {"boolValue": True}},
                    ],
                }
            ]
        )
    )
    a = spans[0].attributes
    assert a["gen_ai.system"] == "openai"
    assert a["gen_ai.request.temperature"] == 0.7
    assert a["gen_ai.request.max_tokens"] == 128
    assert a["stream"] is True


def test_array_value() -> None:
    spans = parse_otlp_json(
        _wrap(
            [
                {
                    "name": "s",
                    "kind": 3,
                    "startTimeUnixNano": "0",
                    "endTimeUnixNano": "1",
                    "attributes": [
                        {
                            "key": "gen_ai.response.finish_reasons",
                            "value": {
                                "arrayValue": {
                                    "values": [
                                        {"stringValue": "stop"},
                                        {"stringValue": "length"},
                                    ]
                                }
                            },
                        }
                    ],
                }
            ]
        )
    )
    assert spans[0].attributes["gen_ai.response.finish_reasons"] == ["stop", "length"]


def test_events() -> None:
    spans = parse_otlp_json(
        _wrap(
            [
                {
                    "name": "s",
                    "kind": 3,
                    "startTimeUnixNano": "0",
                    "endTimeUnixNano": "10",
                    "events": [
                        {
                            "name": "gen_ai.user.message",
                            "timeUnixNano": "5",
                            "attributes": [
                                {"key": "role", "value": {"stringValue": "user"}},
                            ],
                        }
                    ],
                }
            ]
        )
    )
    events = spans[0].events
    assert len(events) == 1
    assert events[0].name == "gen_ai.user.message"
    assert events[0].timestamp_unix_nano == 5
    assert events[0].attributes == {"role": "user"}


def test_multiple_resource_and_scope_spans() -> None:
    def sp(name: str) -> dict[str, Any]:
        return {
            "name": name,
            "kind": 1,
            "startTimeUnixNano": "0",
            "endTimeUnixNano": "1",
        }

    data = {
        "resourceSpans": [
            {"scopeSpans": [{"spans": [sp("a")]}, {"spans": [sp("b")]}]},
            {"scopeSpans": [{"spans": [sp("c")]}]},
        ]
    }
    assert [s.name for s in parse_otlp_json(data)] == ["a", "b", "c"]


def test_parse_from_file(tmp_path: Path) -> None:
    p = tmp_path / "trace.json"
    p.write_text(
        json.dumps(
            _wrap(
                [
                    {
                        "name": "s",
                        "kind": 3,
                        "startTimeUnixNano": "0",
                        "endTimeUnixNano": "1",
                    }
                ]
            )
        )
    )
    spans = parse_otlp_json_file(p)
    assert len(spans) == 1
    assert spans[0].name == "s"


def test_missing_name_raises() -> None:
    with pytest.raises(ValueError, match="name"):
        parse_otlp_json(_wrap([{"kind": 1, "startTimeUnixNano": "0", "endTimeUnixNano": "1"}]))


def test_missing_times_raises() -> None:
    with pytest.raises(ValueError, match="endTimeUnixNano"):
        parse_otlp_json(_wrap([{"name": "s", "kind": 1, "startTimeUnixNano": "0"}]))


def test_unknown_kind_raises() -> None:
    with pytest.raises(ValueError, match="span kind"):
        parse_otlp_json(
            _wrap(
                [
                    {
                        "name": "s",
                        "kind": 99,
                        "startTimeUnixNano": "0",
                        "endTimeUnixNano": "1",
                    }
                ]
            )
        )
