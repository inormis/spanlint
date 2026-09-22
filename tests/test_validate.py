from spanlint.model import InstrumentType, Metric, Span, SpanKind
from spanlint.registry import Registry
from spanlint.validate import Finding, validate, validate_metrics


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
        return [Finding(rule="r", target=span.name, message="boom")]

    result = validate([_span("x")], [failing], _empty_registry())
    assert result == [Finding(rule="r", target="x", message="boom")]


def test_no_rules_produces_no_findings() -> None:
    assert validate([_span("x")], [], _empty_registry()) == []


def test_metric_runner_runs_each_rule_against_each_metric() -> None:
    calls: list[tuple[str, str]] = []

    def rule_a(metric: Metric, _: Registry) -> list[Finding]:
        calls.append(("a", metric.name))
        return []

    def rule_b(metric: Metric, _: Registry) -> list[Finding]:
        calls.append(("b", metric.name))
        return []

    m1 = Metric(name="one", instrument=InstrumentType.HISTOGRAM)
    m2 = Metric(name="two", instrument=InstrumentType.HISTOGRAM)
    validate_metrics([m1, m2], [rule_a, rule_b], _empty_registry())
    assert calls == [("a", "one"), ("b", "one"), ("a", "two"), ("b", "two")]


def test_metric_runner_collects_findings() -> None:
    def failing(metric: Metric, _: Registry) -> list[Finding]:
        return [Finding(rule="r", target=metric.name, message="boom")]

    metric = Metric(name="m", instrument=InstrumentType.HISTOGRAM)
    assert validate_metrics([metric], [failing], _empty_registry()) == [
        Finding(rule="r", target="m", message="boom")
    ]
