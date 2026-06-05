from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Param:
    name: str
    default: str | None = None
    required: bool = False


@dataclass
class Command:
    key: str
    cmd: str
    description: str = ""
    tags: list[str] = field(default_factory=list)

    def params(self) -> list[Param]:
        """Extract parameters from the command template."""
        matches = re.findall(r"\{\{(\w+)(?:::([^}]*))?\}(!?)\}", self.cmd)
        return [
            Param(name=m[0], default=m[1] or None, required=m[2] == "!")
            for m in matches
        ]

    def pretty(self) -> str:
        """Returns the command string formatted for console.print."""
        def replace(match: re.Match) -> str:
            name = match.group(1)
            default = match.group(2)
            required = match.group(3) == "!"
            placeholder = "{{%s%s}%s}" % (
                name,
                f"::{default}" if default else "",
                "!" if required else "",
                )
            color = "yellow" if required else "cyan"
            return f"[{color}]{placeholder}[/{color}]"

        return re.sub(r"\{\{(\w+)(?:::([^}]*))?\}(!?)\}", replace, self.cmd)
