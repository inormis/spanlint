from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .model import AttributeValue, Event, Span, SpanKind, Status, StatusCode

_SPAN_KIND = {
    0: SpanKind.INTERNAL,
    1: SpanKind.INTERNAL,
    2: SpanKind.SERVER,
    3: SpanKind.CLIENT,
    4: SpanKind.PRODUCER,
    5: SpanKind.CONSUMER,
    "SPAN_KIND_UNSPECIFIED": SpanKind.INTERNAL,
    "SPAN_KIND_INTERNAL": SpanKind.INTERNAL,
    "SPAN_KIND_SERVER": SpanKind.SERVER,
    "SPAN_KIND_CLIENT": SpanKind.CLIENT,
    "SPAN_KIND_PRODUCER": SpanKind.PRODUCER,
    "SPAN_KIND_CONSUMER": SpanKind.CONSUMER,
}

_STATUS_CODE = {
    0: StatusCode.UNSET,
    1: StatusCode.OK,
    2: StatusCode.ERROR,
    "STATUS_CODE_UNSET": StatusCode.UNSET,
    "STATUS_CODE_OK": StatusCode.OK,
    "STATUS_CODE_ERROR": StatusCode.ERROR,
}


def parse_otlp_json_file(path: Path) -> list[Span]:
    with path.open() as fh:
        return parse_otlp_json(json.load(fh))


def parse_otlp_json(data: dict[str, Any]) -> list[Span]:
    spans: list[Span] = []
    for rs in data.get("resourceSpans", []):
        for ss in rs.get("scopeSpans", []):
            for raw in ss.get("spans", []):
                spans.append(_parse_span(raw))
    return spans


def _parse_span(raw: dict[str, Any]) -> Span:
    if "name" not in raw:
        raise ValueError("span is missing name")
    return Span(
        name=str(raw["name"]),
        kind=_kind(raw.get("kind", 0)),
        start_time_unix_nano=_int64(raw, "startTimeUnixNano"),
        end_time_unix_nano=_int64(raw, "endTimeUnixNano"),
        attributes=_attributes(raw.get("attributes", [])),
        events=[_parse_event(e) for e in raw.get("events", [])],
        status=_status(raw.get("status", {})),
    )


def _parse_event(raw: dict[str, Any]) -> Event:
    if "name" not in raw:
        raise ValueError("event is missing name")
    return Event(
        name=str(raw["name"]),
        timestamp_unix_nano=_int64(raw, "timeUnixNano"),
        attributes=_attributes(raw.get("attributes", [])),
    )


def _kind(v: Any) -> SpanKind:
    if v in _SPAN_KIND:
        return _SPAN_KIND[v]
    raise ValueError(f"unknown span kind: {v!r}")


def _status(raw: dict[str, Any]) -> Status:
    code_raw = raw.get("code", 0)
    if code_raw not in _STATUS_CODE:
        raise ValueError(f"unknown status code: {code_raw!r}")
    return Status(code=_STATUS_CODE[code_raw], description=str(raw.get("message", "")))


def _int64(raw: dict[str, Any], field: str) -> int:
    if field not in raw:
        raise ValueError(f"span is missing {field}")
    return int(raw[field])


def _attributes(raw: list[dict[str, Any]]) -> dict[str, AttributeValue]:
    out: dict[str, AttributeValue] = {}
    for kv in raw:
        out[str(kv["key"])] = _value(kv["value"])
    return out


def _value(v: dict[str, Any]) -> AttributeValue:
    if "stringValue" in v:
        return str(v["stringValue"])
    if "boolValue" in v:
        return bool(v["boolValue"])
    if "intValue" in v:
        return int(v["intValue"])
    if "doubleValue" in v:
        return float(v["doubleValue"])
    if "arrayValue" in v:
        return _array(v["arrayValue"].get("values", []))
    raise ValueError(f"unsupported attribute value: {v!r}")


def _array(values: list[dict[str, Any]]) -> list[str] | list[bool] | list[int] | list[float]:
    if not values:
        return []
    first = values[0]
    if "stringValue" in first:
        return [str(x["stringValue"]) for x in values]
    if "boolValue" in first:
        return [bool(x["boolValue"]) for x in values]
    if "intValue" in first:
        return [int(x["intValue"]) for x in values]
    if "doubleValue" in first:
        return [float(x["doubleValue"]) for x in values]
    raise ValueError(f"unsupported array element: {first!r}")
