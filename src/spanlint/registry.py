from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AttributeDef:
    id: str
    type: str
    stability: str
    brief: str = ""
    enum_members: tuple[str, ...] = ()


@dataclass
class Registry:
    attributes: dict[str, AttributeDef]

    def attribute(self, name: str) -> AttributeDef | None:
        return self.attributes.get(name)


def load_registry(path: Path) -> Registry:
    attributes: dict[str, AttributeDef] = {}
    for f in _yaml_files(path):
        with f.open() as fh:
            doc = yaml.safe_load(fh) or {}
        for group in doc.get("groups", []):
            for raw in group.get("attributes", []):
                if "ref" in raw:
                    continue
                attr = _parse_attribute(raw)
                attributes[attr.id] = attr
    return Registry(attributes=attributes)


def _yaml_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted([*path.rglob("*.yaml"), *path.rglob("*.yml")])


def _parse_attribute(raw: dict[str, Any]) -> AttributeDef:
    t = raw["type"]
    if isinstance(t, dict) and "members" in t:
        type_str = "enum"
        members = tuple(str(m["id"]) for m in t["members"])
    else:
        type_str = str(t)
        members = ()
    return AttributeDef(
        id=str(raw["id"]),
        type=type_str,
        stability=str(raw.get("stability", "")),
        brief=str(raw.get("brief", "")).strip(),
        enum_members=members,
    )
