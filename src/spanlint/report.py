from __future__ import annotations

import json
from collections.abc import Iterable

from spanlint.validate import Finding


def render_json(findings: Iterable[Finding]) -> str:
    payload = {
        "findings": [{"rule": f.rule, "target": f.target, "message": f.message} for f in findings]
    }
    return json.dumps(payload, indent=2) + "\n"
