from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w

from command_book.models import Command

CONFIG_DIR = Path.home() / ".config" / "command_book"
COMMANDS_FILE = CONFIG_DIR / "commands.toml"


def _validate_key(value: str) -> bool:
    if not value:
        return False
    return " " not in value


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
