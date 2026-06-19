from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum

PARAM_RE = re.compile(r"(?<!\\)\{\{(\w+)(?:::([^}]*))?\}(char|text|path|int|select:[^}!]+)?(!?)\}")  # noqa


class ParamType(str, Enum):
    CHAR = "char"
    TEXT = "text"
    PATH = "path"
    INT = "int"
    SELECT = "select"


@dataclass
class Param:
    name: str
    type: ParamType = ParamType.CHAR
    default: str | None = None
    required: bool = False
    choices: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Missing param name")
        if (self.type == ParamType.INT
                and self.default is not None
                and not self.default.isdigit()):
            raise ValueError("Invalid default value for int param")
        if self.type == ParamType.SELECT and not self.choices:
            raise ValueError(f"Missing choices for select param '{self.name}'")
        if (self.type == ParamType.SELECT
                and self.default is not None
                and self.default not in self.choices):
            raise ValueError(f"Default not in choices for param '{self.name}'")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Param):
            raise NotImplementedError
        return (
            self.name == other.name
            and self.type == other.type
            and self.required == other.required
            and self.choices == other.choices
            )


@dataclass
class Command:
    key: str
    cmd: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    params: list[Param] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if not self.key:
            raise ValueError("Missing key")
        if not self.cmd:
            raise ValueError("Missing cmd")

        seen: dict[str, Param] = {}
        for m in PARAM_RE.finditer(self.cmd):
            name = m.group(1)
            default = m.group(2) or None
            type_raw = m.group(3) or ""
            required = m.group(4) == "!"

            if type_raw.startswith("select:"):
                ptype = ParamType.SELECT
                choices = [c.strip() for c in type_raw[7:].split(",")]
            else:
                ptype = ParamType(type_raw) if type_raw else ParamType.CHAR
                choices = []

            param = Param(
                name=name, type=ptype, default=default,
                required=required, choices=choices)

            if name in seen:
                if seen[name] != param:
                    raise ValueError(f"Wrong param '{name}'")
            else:
                seen[name] = param

        self.params = list(seen.values())

    def pretty(self) -> str:
        def replace(match: re.Match) -> str:
            name = match.group(1)
            default = match.group(2)
            type_raw = match.group(3) or ""
            required = match.group(4) == "!"
            placeholder = "{{%s%s}%s%s}" % (
                name,
                f"::{default}" if default else "",
                type_raw,
                "!" if required else "",
            )
            color = "yellow" if required else "cyan"
            return f"[{color}]{placeholder}[/{color}]"

        result = PARAM_RE.sub(replace, self.cmd)
        return result.replace(r"\{{", "{{")
