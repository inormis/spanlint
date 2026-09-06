from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias

AttributeValue: TypeAlias = (
    str | bool | int | float | list[str] | list[bool] | list[int] | list[float]
)


class SpanKind(Enum):
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class StatusCode(Enum):
    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class Status:
    code: StatusCode = StatusCode.UNSET
    description: str = ""


@dataclass
class Event:
    name: str
    timestamp_unix_nano: int
    attributes: dict[str, AttributeValue] = field(default_factory=dict)


@dataclass
class Span:
    name: str
    kind: SpanKind
    start_time_unix_nano: int
    end_time_unix_nano: int
    attributes: dict[str, AttributeValue] = field(default_factory=dict)
    events: list[Event] = field(default_factory=list)
    status: Status = field(default_factory=Status)
