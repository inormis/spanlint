from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from spanlint.model import Span
from spanlint.registry import Registry


@dataclass
class Finding:
    rule: str
    span: str
    message: str


Rule = Callable[[Span, Registry], list[Finding]]


def validate(spans: Iterable[Span], rules: Iterable[Rule], registry: Registry) -> list[Finding]:
    findings: list[Finding] = []
    for span in spans:
        for rule in rules:
            findings.extend(rule(span, registry))
    return findings
