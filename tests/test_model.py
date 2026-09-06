from spanlint.model import Event, Span, SpanKind, Status, StatusCode


def test_span_defaults() -> None:
    span = Span(
        name="chat",
        kind=SpanKind.CLIENT,
        start_time_unix_nano=1_000,
        end_time_unix_nano=2_000,
    )
    assert span.attributes == {}
    assert span.events == []
    assert span.status == Status(code=StatusCode.UNSET, description="")


def test_span_with_attributes_and_events() -> None:
    events = [
        Event(
            name="gen_ai.user.message",
            timestamp_unix_nano=1_500,
            attributes={"role": "user"},
        ),
    ]
    span = Span(
        name="chat",
        kind=SpanKind.CLIENT,
        start_time_unix_nano=1_000,
        end_time_unix_nano=2_000,
        attributes={"gen_ai.system": "openai"},
        events=events,
        status=Status(code=StatusCode.OK),
    )
    assert span.attributes["gen_ai.system"] == "openai"
    assert span.events[0].name == "gen_ai.user.message"
    assert span.status.code is StatusCode.OK


def test_span_equality() -> None:
    a = Span(name="x", kind=SpanKind.INTERNAL, start_time_unix_nano=0, end_time_unix_nano=1)
    b = Span(name="x", kind=SpanKind.INTERNAL, start_time_unix_nano=0, end_time_unix_nano=1)
    assert a == b


def test_event_defaults() -> None:
    event = Event(name="gen_ai.choice", timestamp_unix_nano=42)
    assert event.attributes == {}


def test_enum_values() -> None:
    assert SpanKind.CLIENT.value == "client"
    assert StatusCode.ERROR.value == "error"
