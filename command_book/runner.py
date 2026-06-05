from __future__ import annotations

import re
import subprocess

from command_book.models import Param


def resolve(cmd: str, params: list[Param], values: dict[str, str]) -> str:
    """Replace placeholders with the provided values."""

    def replacer(match: re.Match) -> str:
        name = match.group(1)
        return values.get(name, match.group(2) or "")

    return re.sub(r"\{\{(\w+)(?:::([^}]*))?\}\}", replacer, cmd)


def execute(cmd: str) -> int:
    """Run the command in the system shell."""
    result = subprocess.run(cmd, shell=True)
    return result.returncode
