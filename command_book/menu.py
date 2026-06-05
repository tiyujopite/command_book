from __future__ import annotations

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console

from command_book import runner, store
from command_book.i18n import _
from command_book.models import Command

console = Console()


def _ask_params(command: Command) -> dict[str, str]:
    values: dict[str, str] = {}
    for param in command.params():
        if param.required:
            prompt = f"{param.name} {_('param_required')}"
        else:
            prompt = f"{param.name} [{param.default}]"
        value: str = inquirer.text(message=prompt + ":").execute()
        if not value and not param.required:
            value = param.default or ""
        values[param.name] = value
    return values


def run_menu() -> None:
    commands = store.load_all()
    if not commands:
        console.print(f"[yellow]{_('menu_empty')}[/yellow]")
        return

    cmd_map = {cmd.key: cmd for cmd in commands}

    choices = [Choice(
            value=cmd.key,
            name=f"{cmd.key:<20} {cmd.description:<35} {', '.join(cmd.tags)}",
            ) for cmd in commands]

    selected_key: str | None = inquirer.fuzzy(
        message=_("menu_title"),
        choices=choices,
        max_height="70%",
        instruction=_("menu_instruction"),
        ).execute()

    if selected_key is None:
        return

    selected = cmd_map[selected_key]
    params = selected.params()
    if params:
        console.print(f"\n[bold]{selected.key}[/bold] {_('menu_fill_params')}")
        console.rule()
        values = _ask_params(selected)
    else:
        values = {}

    resolved = runner.resolve(selected.cmd, params, values)
    console.rule()
    console.print(f"[green]{_('run_executing')}[/green] {resolved}")
    runner.execute(resolved)
