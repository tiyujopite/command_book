from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner as TyperRunner

import command_book.cli as cli_module
from command_book import store
from command_book.cli import _complete_key, app
from command_book.models import Command

typer_runner = TyperRunner()


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    config_dir = tmp_path / "command_book"
    commands_file = config_dir / "commands.toml"
    monkeypatch.setattr(store, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(store, "COMMANDS_FILE", commands_file)
    monkeypatch.setattr(cli_module, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(cli_module, "COMMANDS_FILE", commands_file)


def test_complete_key_matches():
    store.save(Command(key="git-status", cmd="git status"))
    store.save(Command(key="git-log", cmd="git log"))
    store.save(Command(key="docker-ps", cmd="docker ps"))
    result = _complete_key("git")
    assert "git-status" in result
    assert "git-log" in result
    assert "docker-ps" not in result


def test_complete_key_no_matches():
    store.save(Command(key="ssh-server", cmd="ssh ..."))
    assert _complete_key("xyz") == []


def test_list_empty():
    result = typer_runner.invoke(app, ["list"])
    assert result.exit_code == 0


def test_list_with_commands():
    store.save(Command(key="my-cmd", cmd="echo hi", description="Hi"))
    result = typer_runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "my-cmd" in result.output


def test_remove_existing():
    store.save(Command(key="del-cmd", cmd="echo bye"))
    result = typer_runner.invoke(app, ["remove", "del-cmd"])
    assert result.exit_code == 0
    assert store.load_one("del-cmd") is None


def test_remove_not_found():
    result = typer_runner.invoke(app, ["remove", "ghost"])
    assert result.exit_code == 1


def test_search_with_results():
    store.save(Command(key="git-status", cmd="git status", tags=["git"]))
    result = typer_runner.invoke(app, ["search", "git"])
    assert result.exit_code == 0
    assert "git-status" in result.output


def test_search_by_description():
    store.save(Command(key="my-cmd", cmd="echo hi", description="Unique"))
    result = typer_runner.invoke(app, ["search", "unique"])
    assert result.exit_code == 0
    assert "my-cmd" in result.output


def test_search_by_tag():
    store.save(Command(key="docker-ps", cmd="docker ps", tags=["docker"]))
    result = typer_runner.invoke(app, ["search", "docker"])
    assert result.exit_code == 0
    assert "docker-ps" in result.output


def test_search_no_results():
    result = typer_runner.invoke(app, ["search", "zzznomatch"])
    assert result.exit_code == 0


def test_tags_empty():
    result = typer_runner.invoke(app, ["tags"])
    assert result.exit_code == 0


def test_tags_with_data():
    store.save(Command(key="a", cmd="echo", tags=["infra", "ssh"]))
    result = typer_runner.invoke(app, ["tags"])
    assert result.exit_code == 0
    assert "infra" in result.output
    assert "ssh" in result.output


def _text_mock(side_effects: list) -> MagicMock:
    m = MagicMock()
    m.return_value.execute = MagicMock(side_effect=side_effects)
    return m


def test_add():
    text_mock = _text_mock(["new-cmd", "echo hello", "A", "tag1, tag2"])
    with patch("InquirerPy.inquirer.text", text_mock):
        result = typer_runner.invoke(app, ["add"])
    assert result.exit_code == 0
    saved = store.load_one("new-cmd")
    assert saved is not None
    assert saved.cmd == "echo hello"
    assert saved.tags == ["tag1", "tag2"]


def test_add_no_tags():
    text_mock = _text_mock(["simple-cmd", "ls -la", "List files", ""])
    with patch("InquirerPy.inquirer.text", text_mock):
        result = typer_runner.invoke(app, ["add"])
    assert result.exit_code == 0
    saved = store.load_one("simple-cmd")
    assert saved is not None
    assert saved.tags == []


def test_run_not_found():
    result = typer_runner.invoke(app, ["run", "ghost"])
    assert result.exit_code == 1


def test_run_no_params():
    store.save(Command(key="simple", cmd="echo hi"))
    with patch("command_book.runner.execute", return_value=0):
        result = typer_runner.invoke(app, ["run", "simple"])
    assert result.exit_code == 0


def test_run_with_required_param():
    store.save(Command(key="ssh-cmd", cmd="ssh {{host}!}"))
    text_mock = _text_mock(["myserver"])
    with patch("InquirerPy.inquirer.text", text_mock), \
         patch("command_book.runner.execute", return_value=0):
        result = typer_runner.invoke(app, ["run", "ssh-cmd"])
    assert result.exit_code == 0
    assert "myserver" in result.output


def test_run_with_optional_param_uses_default():
    store.save(Command(key="ssh-def", cmd="ssh {{host}} -p {{port::22}}"))
    # host filled, port skipped → uses default
    text_mock = _text_mock(["myserver", ""])
    with patch("InquirerPy.inquirer.text", text_mock), \
         patch("command_book.runner.execute", return_value=0):
        result = typer_runner.invoke(app, ["run", "ssh-def"])
    assert result.exit_code == 0
    assert "22" in result.output


def test_edit_not_found():
    result = typer_runner.invoke(app, ["edit", "ghost"])
    assert result.exit_code == 1


def test_edit_same_key():
    store.save(Command(key="orig", cmd="echo old", description="Old"))
    text_mock = _text_mock(["echo new", "New desc", "y"])
    with patch("InquirerPy.inquirer.text", text_mock):
        result = typer_runner.invoke(app, ["edit", "orig"])
    assert result.exit_code == 0
    updated = store.load_one("orig")
    assert updated is not None
    assert updated.cmd == "echo new"
    assert updated.description == "New desc"
    assert updated.tags == ["y"]


def test_config_creates_file_if_missing(tmp_path):
    result = typer_runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert cli_module.COMMANDS_FILE.exists()
    assert str(cli_module.COMMANDS_FILE) in result.output


def test_config_shows_path_if_exists():
    cli_module.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cli_module.COMMANDS_FILE.write_text("[commands]\n")
    result = typer_runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert str(cli_module.COMMANDS_FILE) in result.output
