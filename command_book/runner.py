from __future__ import annotations

import os
import re
import subprocess

from InquirerPy import inquirer
from rich.console import Console

from command_book.i18n import _
from command_book.models import Command, Param

console = Console()


def ask_params(command: Command) -> dict[str, str]:
    values: dict[str, str] = {}
    console.print(f"> {command.pretty()}")
    for param in command.params():
        prompt = param.name
        if param.default:
            prompt += f" [{param.default}]"
        elif param.required:
            prompt += f" ({_('required')})"
        value: str = ""
        while not value:
            value: str = inquirer.text(message=prompt + ":").execute()
            if not value:
                value = param.default or ""
            if not param.required:
                break
        values[param.name] = value
    return values


def resolve(cmd: str, params: list[Param], values: dict[str, str]) -> str:
    """Replace placeholders with the provided values."""

    def replacer(match: re.Match) -> str:
        name = match.group(1)
        return values.get(name, match.group(2) or "")

    return re.sub(r"\{\{(\w+)(?:::([^}]*))?\}(!?)\}", replacer, cmd)


def execute(cmd: str) -> int:
    """Run the command in the system shell."""
    executable = os.environ.get("SHELL", "/bin/sh") or None
    result = subprocess.run(cmd, shell=True, executable=executable)
    return result.returncode
