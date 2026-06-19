from __future__ import annotations

import os
import re
import subprocess

from InquirerPy import inquirer
from rich.console import Console
from rich.panel import Panel

from command_book.i18n import _
from command_book.models import PARAM_RE, Command, Param, ParamType

console = Console()


def _ask_params(params: list[Param]) -> dict[str, str]:
    values: dict[str, str] = {}
    for param in params:
        prompt = param.name
        if param.default:
            prompt += f" [{param.default}]"
        elif param.required:
            prompt += f" ({_('required')})"
        prompt += ":"

        value: str = ""
        while not value:
            match param.type:
                case ParamType.TEXT:
                    value = inquirer.text(
                        message=prompt,
                        multiline=True,
                        default=param.default or "",
                        ).execute()
                    value = value.rstrip("\n")

                case ParamType.PATH:
                    value = inquirer.filepath(
                        message=prompt,
                        default=param.default or "",
                        ).execute()

                case ParamType.INT:
                    value = inquirer.text(
                        message=prompt,
                        default=param.default or "",
                        validate=lambda v: v.lstrip("-").isdigit(),
                        invalid_message=_("invalid_int"),
                        ).execute()

                case ParamType.SELECT:
                    value = inquirer.select(
                        message=prompt,
                        choices=param.choices,
                        default=param.default,
                        ).execute()

                case _:  # CHAR
                    value = inquirer.text(
                        message=prompt,
                        default=param.default or "",
                        ).execute()

            if not param.required:
                break

        values[param.name] = value

    return values


def _resolve(cmd: str, params: list[Param], values: dict[str, str]) -> str:
    """Replace placeholders with the provided values."""

    def replacer(match: re.Match) -> str:
        name = match.group(1)
        return values.get(name, match.group(2) or "")

    result = re.sub(PARAM_RE, replacer, cmd)
    return result.replace(r"\{{", "{{")


def _execute(cmd: str) -> int:
    """Run the command in the system shell."""
    executable = os.environ.get("SHELL", "/bin/sh") or None
    result = subprocess.run(cmd, shell=True, executable=executable)
    return result.returncode


def execute_command(command: Command) -> None:
    """Ask for parameters, resolve the command and execute it."""
    params = command.params
    values = []
    if params:
        values = _ask_params(params)
    resolved = _resolve(command.cmd, params, values)
    console.print(Panel(
            f"[green]{_('run_executing')}[/green] {resolved}", expand=False,
            border_style="green"))
    _execute(resolved)
