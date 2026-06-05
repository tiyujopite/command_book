from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Param:
    name: str
    default: str | None = None

    @property
    def required(self) -> bool:
        return self.default is None


@dataclass
class Command:
    key: str
    cmd: str
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def params(self) -> list[Param]:
        """Extract parameters from the command template."""
        matches = re.findall(r"\{\{(\w+)(?:::([^}]*))?\}\}", self.cmd)
        return [Param(name=m[0], default=m[1] or None) for m in matches]
