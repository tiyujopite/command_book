from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w
import typer
from InquirerPy import inquirer
from rich.console import Console

from command_book.i18n import _
from command_book.models import Command

CONFIG_DIR = Path.home() / ".config" / "command_book"
COMMANDS_FILE = CONFIG_DIR / "commands.toml"
console = Console()


def _validate_key(value: str) -> bool:
    if not value:
        return False
    return " " not in value


def _validate_new_key(value: str) -> bool:
    if not _validate_key(value):
        return False
    if load_one(value) is not None:
        return False
    return True


def _load_raw() -> dict[str, dict]:
    if not COMMANDS_FILE.exists():
        return {}
    with open(COMMANDS_FILE, "rb") as f:
        data = tomllib.load(f)
    return data.get("commands", {})


def _save_raw(commands: dict[str, dict]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(COMMANDS_FILE, "wb") as f:
        tomli_w.dump({"commands": commands}, f)


def load_all() -> list[Command]:
    raw = _load_raw()
    commands = []
    for key, data in raw.items():
        if not _validate_key(key):  # pragma: no cover
            continue
        commands.append(Command(
                key=key,
                cmd=data.get("cmd", ""),
                description=data.get("description", ""),
                tags=list(data.get("tags", [])),
                ))
    return commands


def load_one(key: str) -> Command | None:
    raw = _load_raw()
    if key not in raw:
        return None
    data = raw[key]
    return Command(
        key=key,
        cmd=data.get("cmd", ""),
        description=data.get("description", ""),
        tags=list(data.get("tags", [])),
        )


def save(command: Command) -> None:
    raw = _load_raw()
    raw[command.key] = {
        "cmd": command.cmd,
        "description": command.description,
        "tags": command.tags,
        }
    _save_raw(raw)


def remove(key: str) -> bool:
    raw = _load_raw()
    if key not in raw:
        return False
    del raw[key]
    _save_raw(raw)
    return True


def add_edit(key: str | None) -> None:
    new = key is None
    if not new:
        command = load_one(key)
        if command is None:
            console.print(f"[red]{_('run_not_found').format(key=key)}[/red]")
            raise typer.Exit(1)
        cmd = command.cmd
        description = command.description
        tags = ", ".join(command.tags)
    else:
        cmd, description, tags = "", "", ""

    while not key:
        key: str = inquirer.text(
            message=_("add_prompt_key"),
            validate=_validate_new_key,
            invalid_message=_("key_invalid"),
            ).execute()
    if new:
        console.print(
            Command(key="example", cmd=_("add_example_cmd")).pretty())
    cmd = inquirer.text(
        message=_("add_prompt_cmd"), multiline=True, default=cmd
        ).execute()
    cmd = cmd.rstrip("\n")
    description = inquirer.text(
        message=_("add_prompt_description"), default=description
        ).execute()
    tags_raw = inquirer.text(
        message=_("add_prompt_tags"), default=tags
        ).execute()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    command = Command(key=key, cmd=cmd, description=description, tags=tags)
    save(command)
    console.print(f"[green]{_('add_saved').format(key=key)}[/green]")
