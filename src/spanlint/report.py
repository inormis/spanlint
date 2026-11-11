from __future__ import annotations

import json
from collections.abc import Iterable

from spanlint.validate import Finding


def render_json(findings: Iterable[Finding]) -> str:
    payload = {
        "findings": [{"rule": f.rule, "target": f.target, "message": f.message} for f in findings]
    }
    return json.dumps(payload, indent=2) + "\n"


def render_text(findings: Iterable[Finding]) -> str:
    items = list(findings)
    if not items:
        return "no findings\n"
    lines = [f"{f.target}: {f.message} [{f.rule}]" for f in items]
    noun = "finding" if len(items) == 1 else "findings"
    lines.append(f"{len(items)} {noun}")
    return "\n".join(lines) + "\n"


def render_matrix(matrix: dict[str, dict[str, int]]) -> str:
    """Render a framework-by-rule findings matrix as a markdown table."""
    rules = sorted({rule for counts in matrix.values() for rule in counts})
    lines = [
        "| framework | " + " | ".join(rules) + " |" if rules else "| framework |",
        "| --- |" + " ---: |" * len(rules),
    ]
    for framework, counts in matrix.items():
        cells = [str(counts[rule]) if counts.get(rule) else "" for rule in rules]
        lines.append("| " + " | ".join([framework, *cells]) + " |")
    return "\n".join(lines) + "\n"
