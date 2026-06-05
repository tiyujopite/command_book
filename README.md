# Command Book (`bb`)

CLI to save, search and run custom commands with interactive parameters.

## Installation

```bash
pip install command-book
bb --install-completion
# reload console
```

## Usage

```bash
bb                      # Open the interactive fuzzy menu
bb add                  # Register a new command
bb list                 # List all saved commands
bb run <name>           # Run a command (prompts for parameters if needed)
bb remove <name>        # Delete a command
bb edit <name>          # Open the command in $EDITOR
bb search <term>        # Search by name, description or tag
bb tags                 # List all available tags
bb config               # Show or edit the config file
bb --install-completion # Install shell completion
```

## Command format

Commands use placeholders `{{name}}` or `{{name::default}}`:

```toml
[commands.ssh-server]
cmd = "ssh {{user::root}}@{{host}} -p {{port::22}}"
description = "Connect to a server via SSH"
tags = ["ssh", "infra"]
```

## Storage

Commands are saved to `~/.config/command_book/commands.toml`.

## Language

By default the language is detected from the `LANG` environment variable.
Override it with `CB_LANG`:

```bash
CB_LANG=en bb   # English
CB_LANG=es bb   # Spanish
```

## Development

```bash
git clone https://github.com/tiyujopite/command_book
cd command-book
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest --cov=command_book   # Run tests with coverage
flake8 command_book/        # Linting
```
