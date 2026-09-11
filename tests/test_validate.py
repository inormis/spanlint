from spanlint.model import Span, SpanKind
from spanlint.registry import Registry
from spanlint.validate import Finding, validate


def _empty_registry() -> Registry:
    return Registry(attributes={})


def _span(name: str) -> Span:
    return Span(name=name, kind=SpanKind.CLIENT, start_time_unix_nano=0, end_time_unix_nano=1)


def test_runs_each_rule_against_each_span() -> None:
    calls: list[tuple[str, str]] = []

    def rule_a(span: Span, _: Registry) -> list[Finding]:
        calls.append(("a", span.name))
        return []

    def rule_b(span: Span, _: Registry) -> list[Finding]:
        calls.append(("b", span.name))
        return []

    validate([_span("one"), _span("two")], [rule_a, rule_b], _empty_registry())
    assert calls == [("a", "one"), ("b", "one"), ("a", "two"), ("b", "two")]


def test_collects_findings_from_all_rules() -> None:
    def failing(span: Span, _: Registry) -> list[Finding]:
        return [Finding(rule="r", span=span.name, message="boom")]

    result = validate([_span("x")], [failing], _empty_registry())
    assert result == [Finding(rule="r", span="x", message="boom")]


def test_no_rules_produces_no_findings() -> None:
    assert validate([_span("x")], [], _empty_registry()) == []
