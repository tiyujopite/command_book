from unittest.mock import MagicMock, patch

import pytest

from command_book import store
from command_book.menu import _ask_params, run_menu
from command_book.models import Command


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "CONFIG_DIR", tmp_path / "command_book")
    monkeypatch.setattr(
        store, "COMMANDS_FILE", tmp_path / "command_book" / "commands.toml")


def test_ask_params_required():
    cmd = Command(key="test", cmd="ssh {{host}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "myserver"
    with patch("command_book.menu.inquirer.text", text_mock):
        values = _ask_params(cmd)
    assert values == {"host": "myserver"}


def test_ask_params_optional_with_value():
    cmd = Command(key="test", cmd="ssh -p {{port::22}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "2222"
    with patch("command_book.menu.inquirer.text", text_mock):
        values = _ask_params(cmd)
    assert values == {"port": "2222"}


def test_ask_params_optional_empty_uses_default():
    cmd = Command(key="test", cmd="ssh -p {{port::22}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = ""
    with patch("command_book.menu.inquirer.text", text_mock):
        values = _ask_params(cmd)
    assert values == {"port": "22"}


def test_run_menu_empty():
    with patch("command_book.menu.console.print") as mock_print:
        run_menu()
    mock_print.assert_called_once()


def test_run_menu_user_cancels():
    store.save(Command(key="my-cmd", cmd="echo hi"))
    fuzzy_mock = MagicMock()
    fuzzy_mock.return_value.execute.return_value = None
    with patch("command_book.menu.inquirer.fuzzy", fuzzy_mock):
        run_menu()  # should return without error


def test_run_menu_select_no_params():
    store.save(Command(key="my-cmd", cmd="echo hi"))
    fuzzy_mock = MagicMock()
    fuzzy_mock.return_value.execute.return_value = "my-cmd"
    with patch("command_book.menu.inquirer.fuzzy", fuzzy_mock), \
         patch("command_book.runner.execute", return_value=0):
        run_menu()


def test_run_menu_select_with_params():
    store.save(Command(key="ssh-cmd", cmd="ssh {{host}}"))
    fuzzy_mock = MagicMock()
    fuzzy_mock.return_value.execute.return_value = "ssh-cmd"
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "myserver"
    with patch("command_book.menu.inquirer.fuzzy", fuzzy_mock), \
         patch("command_book.menu.inquirer.text", text_mock), \
         patch("command_book.runner.execute", return_value=0):
        run_menu()
