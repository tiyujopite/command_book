from __future__ import annotations

import os

import typer
from InquirerPy import inquirer
from rich.console import Console
from rich.table import Table

from command_book import runner, store
from command_book.i18n import _
from command_book.menu import run_menu
from command_book.models import Command
from command_book.store import COMMANDS_FILE, CONFIG_DIR, _validate_new_key

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


def _build_commands_table(commands: list[Command]) -> Table:
    table = Table(show_header=True, header_style="bold", show_lines=True,
        expand=True)
    table.add_column(_("col_key"), style="cyan")
    table.add_column(_("col_description"))
    table.add_column(_("col_tags"), style="dim")
    for cmd in commands:
        desc = (
            f"\n[italic]{cmd.description}[/italic]" if cmd.description else "")
        table.add_row(
            cmd.key,
            cmd.pretty() + desc,
            ", ".join(cmd.tags)
            )
    return table


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        run_menu()  # pragma: no cover


@app.command(help=_("add_help"))
def add() -> None:
    key: str = ''
    while not key:
        key: str = inquirer.text(
            message=_("add_prompt_key"),
            validate=_validate_new_key,
            invalid_message=_("key_invalid"),
            ).execute()
    console.print(Command(key="example", cmd=_("add_example_cmd")).pretty())
    cmd: str = inquirer.text(message=_("add_prompt_cmd"), multiline=True,
        ).execute()
    cmd = cmd.rstrip("\n")
    description: str = inquirer.text(
        message=_("add_prompt_description")).execute()
    tags_raw: str = inquirer.text(message=_("add_prompt_tags")).execute()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    command = Command(key=key, cmd=cmd, description=description, tags=tags)
    store.save(command)
    console.print(f"[green]{_('add_saved').format(key=key)}[/green]")


@app.command("list", help=_("list_help"))
def list_commands() -> None:
    commands = store.load_all()
    if not commands:
        console.print(f"[yellow]{_('list_empty')}[/yellow]")
        return

    console.print(_build_commands_table(commands))


@app.command(help=_("run_help"))
def run(key: str = _key_arg(_("run_arg_help"))) -> None:
    command = store.load_one(key)
    if command is None:
        console.print(f"[red]{_('run_not_found').format(key=key)}[/red]")
        raise typer.Exit(1)

    values = runner.ask_params(command)
    resolved = runner.resolve(command.cmd, command.params(), values)
    console.print(f"[green]{_('run_executing')}[/green] {resolved}")
    console.print(f"[green]{'-' * 50}[/green]")
    runner.execute(resolved)


@app.command(help=_("remove_help"))
def remove(key: str = _key_arg(_("remove_arg_help"))) -> None:
    if store.remove(key):
        console.print(
            f"[green]{_('remove_deleted').format(key=key)}[/green]")
    else:
        console.print(
            f"[red]{_('remove_not_found').format(key=key)}[/red]")
        raise typer.Exit(1)


@app.command(help=_("edit_help"))
def edit(key: str = _key_arg(_("edit_arg_help"))) -> None:
    command = store.load_one(key)
    if command is None:
        console.print(f"[red]{_('run_not_found').format(key=key)}[/red]")
        raise typer.Exit(1)

    cmd: str = inquirer.text(message=_("add_prompt_cmd"), multiline=True,
        default=command.cmd
        ).execute()
    cmd = cmd.rstrip("\n")
    description: str = inquirer.text(
        message=_("add_prompt_description"), default=command.description
        ).execute()
    tags_raw: str = inquirer.text(
        message=_("add_prompt_tags"), default=", ".join(command.tags)
        ).execute()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    updated = Command(key=key, cmd=cmd, description=description, tags=tags)
    store.save(updated)
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

    console.print(_build_commands_table(results))


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
