from rich import box
from rich.panel import Panel
from rich.table import Table

from command_book.i18n import _
from command_book.models import Command


def build_commands_table(commands: list[Command]) -> Panel:
    table = Table(
        box=box.HORIZONTALS, show_header=False, padding=(0, 2, 0, 0),
        expand=True, show_edge=False,
        )
    table.add_column(style="cyan", no_wrap=True)
    table.add_column()
    table.add_column(style="dim")

    for cmd in commands:
        description = (
            f"[cyan][italic]{cmd.description}[/italic][/cyan]\n"
            if cmd.description else ""
            )
        table.add_row(
            cmd.key,
            description + cmd.pretty(),
            ", ".join(cmd.tags),
            )
        table.add_section()

    return Panel(table, title=_("list_title"), expand=True)


def build_examples_panel() -> Panel:
    rows = [
        (_("examples_char"), "{{name}}"),
        (_("examples_default"), "{{name::world}}"),
        (_("examples_required"), "{{name}!}"),
        (_("examples_text"), "{{body}text}"),
        (_("examples_path"), "{{file}path}"),
        (_("examples_int"), "{{port}int}"),
        (_("examples_select"), "{{env}select:dev,staging,prod}"),
        ]

    table = Table(box=None, show_header=False, padding=(0, 2, 0, 0),
        expand=True)
    table.add_column(no_wrap=True)
    table.add_column()

    for description, syntax in rows:
        table.add_row(Command(key="x", cmd=syntax).pretty(), description)

    return Panel(table, title=_("examples_title"), expand=True)


def build_command_panel(command: Command) -> Panel:
    desc = (f"[cyan][italic]{command.description}[/italic][/cyan]\n"
        if command.description else "")
    return Panel(desc + command.pretty(), expand=False)
