from unittest.mock import patch

import pytest
import typer

from command_book import store
from command_book.models import Command
from command_book.store import _validate_key, _validate_new_key


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    """Redirige el archivo de configuración a un directorio temporal."""
    config_dir = tmp_path / "command_book"
    monkeypatch.setattr(store, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(store, "COMMANDS_FILE", config_dir / "commands.toml")


def test_save_and_load_one():
    cmd = Command(
        key="test-cmd", cmd="echo hello", description="Test", tags=["test"])
    store.save(cmd)
    loaded = store.load_one("test-cmd")
    assert loaded is not None
    assert loaded.key == "test-cmd"
    assert loaded.cmd == "echo hello"
    assert loaded.description == "Test"
    assert loaded.tags == ["test"]


def test_load_one_missing():
    assert store.load_one("nonexistent") is None


def test_load_all_empty():
    assert store.load_all() == []


def test_load_all_multiple():
    store.save(Command(key="a", cmd="echo a", description="A", tags=[]))
    store.save(Command(key="b", cmd="echo b", description="B", tags=["x"]))
    commands = store.load_all()
    keys = {c.key for c in commands}
    assert keys == {"a", "b"}


def test_remove_existing():
    store.save(Command(key="del-me", cmd="echo bye"))
    with patch("command_book.store.inquirer.select") as select_mock:
        select_mock.return_value.execute.return_value = True
        assert store.remove("del-me") is True
    assert store.load_one("del-me") is None


def test_remove_existing_cancelled():
    store.save(Command(key="del-me", cmd="echo bye"))
    with patch("command_book.store.inquirer.select") as select_mock:
        select_mock.return_value.execute.return_value = False
        assert store.remove("del-me") is False
    assert store.load_one("del-me") is not None


def test_remove_missing():
    with pytest.raises(typer.Exit):
        store.remove("ghost")


def test_save_overwrites():
    store.save(Command(key="dup", cmd="echo first"))
    store.save(Command(key="dup", cmd="echo second"))
    loaded = store.load_one("dup")
    assert loaded is not None
    assert loaded.cmd == "echo second"


def test_validate_new_key_invalid_key():
    assert _validate_new_key("bad key") is False
    assert _validate_new_key("") is False


def test_validate_new_key_existing():
    store.save(Command(key="existing", cmd="echo hi"))
    assert _validate_new_key("existing") is False


def test_validate_new_key_valid():
    assert _validate_new_key("brand-new") is True


def test_validate_key_valid():
    assert _validate_key("git-status") is True
    assert _validate_key("my_cmd") is True
    assert _validate_key("cmd123") is True


def test_validate_key_with_space():
    assert _validate_key("git status") is False
    assert _validate_key(" leading") is False
    assert _validate_key("trailing ") is False


def test_validate_key_empty():
    assert _validate_key("") is False


def test_validate_new_key_existing_other_key():
    store.save(Command(key="taken", cmd="echo"))
    assert store._validate_new_key("taken", editing=None) is False
    assert store._validate_new_key("taken", editing="taken") is True
