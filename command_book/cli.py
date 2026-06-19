from __future__ import annotations

import os

import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console

from command_book import runner, store
from command_book.i18n import _
from command_book.store import COMMANDS_FILE, CONFIG_DIR
from command_book.tools import (build_command_panel, build_commands_table,
                                build_examples_panel)

app = typer.Typer(
    name="bb",
    help=_("app_help"),
    invoke_without_command=True,
    )

console = Console()


def _complete_key(incomplete: str) -> list[str]:
    commands = store.load_all()
    return [cmd.key for cmd in commands if cmd.key.startswith(incomplete)]


def _key_arg(help: str) -> typer.Argument:
    return typer.Argument(..., help=help, autocompletion=_complete_key)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:  # pragma: no cover
    if ctx.invoked_subcommand is not None:
        return
    commands = store.load_all()
    if not commands:
        console.print(f"[yellow]{_('menu_empty')}[/yellow]")
        return

    cmd_map = {cmd.key: cmd for cmd in commands}

    choices = []
    for cmd in commands:
        name = f"{cmd.key:<25} {cmd.description:<50}"
        choices.append(Choice(value=cmd.key, name=name))
    choices.append(Choice(value=None, name=f"{_('menu_exit')}"))

    selected_key: str | None = inquirer.fuzzy(
        message=_("menu_title"),
        choices=choices,
        max_height="70%",
        instruction=_("menu_instruction"),
        ).execute()

    if selected_key is None:
        return

    selected = cmd_map[selected_key]

    console.print(build_command_panel(selected))

    action: str | None = inquirer.select(
        message=_("menu_action"),
        choices=[
            Choice(value="run", name=_("menu_action_run")),
            Choice(value="edit", name=_("menu_action_edit")),
            Choice(value="remove", name=_("menu_action_remove")),
            Choice(value=None, name=_("menu_exit")),
            ],
        default="run",
        ).execute()

    match action:
        case "run":
            run(selected.key)
        case "edit":
            edit(selected.key)
        case "remove":
            remove(selected.key)
        case _:
            return


@app.command(help=_("add_help"))
def add() -> None:
    if store.add_edit(None):
        console.print(f"[green]{_('add_saved')}[/green]")


@app.command("list", help=_("list_help"))
def list_commands() -> None:
    commands = store.load_all()
    if not commands:
        console.print(f"[yellow]{_('list_empty')}[/yellow]")
        return

    console.print(build_commands_table(commands))


@app.command(help=_("run_help"))
def run(key: str = _key_arg(_("run_arg_help"))) -> None:
    command = store.load_one(key)
    if command is None:
        console.print(f"[red]{_('run_not_found').format(key=key)}[/red]")

    console.print(build_command_panel(command))
    runner.execute_command(command)


@app.command(help=_("remove_help"))
def remove(key: str = _key_arg(_("remove_arg_help"))) -> None:
    if store.remove(key):
        console.print(f"[green]{_('remove_deleted').format(key=key)}[/green]")


@app.command(help=_("edit_help"))
def edit(key: str = _key_arg(_("edit_arg_help"))) -> None:
    if store.add_edit(key):
        console.print(f"[green]{_('edit_saved').format(key=key)}[/green]")


@app.command(help=_("search_help"))
def search(term: str = typer.Argument(..., help=_("search_arg_help"))) -> None:
    commands = store.load_all()
    term = term.lower()
    results = [
        cmd
        for cmd in commands
        if term in cmd.key.lower()
        or term in cmd.cmd.lower()
        or term in cmd.description.lower()
        or any(term in tag.lower() for tag in cmd.tags)
        ]

    if not results:
        console.print(
            f"[yellow]{_('search_no_results').format(term=term)}[/yellow]")
        return

    console.print(build_commands_table(results))


@app.command(help=_("tags_help"))
def tags() -> None:
    commands = store.load_all()
    all_tags = sorted({tag for cmd in commands for tag in cmd.tags})

    if not all_tags:
        console.print(f"[yellow]{_('tags_empty')}[/yellow]")
        return

    for tag in all_tags:
        console.print(f"  [cyan]{tag}[/cyan]")


@app.command(help=_("config_help"))
def config(
        edit: bool = typer.Option(False, "--edit", "-e", help=_("Open file")),
        ) -> None:
    if not COMMANDS_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        COMMANDS_FILE.write_text("[commands]\n")
        console.print(f"[yellow]{_('config_created')}[/yellow]")

    console.print(_("config_file").format(path=""))
    console.out(str(COMMANDS_FILE))

    if edit:  # pragma: no cover
        editor = os.environ.get("EDITOR", "nano")
        os.execlp(editor, editor, str(COMMANDS_FILE))


@app.command(help=_("examples_help"))
def examples() -> None:
    console.print(build_examples_panel())
