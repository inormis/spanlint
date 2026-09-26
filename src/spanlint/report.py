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
