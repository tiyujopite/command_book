import pytest

from command_book import store
from command_book.models import Command


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
    assert store.remove("del-me") is True
    assert store.load_one("del-me") is None


def test_remove_missing():
    assert store.remove("ghost") is False


def test_save_overwrites():
    store.save(Command(key="dup", cmd="echo first"))
    store.save(Command(key="dup", cmd="echo second"))
    loaded = store.load_one("dup")
    assert loaded is not None
    assert loaded.cmd == "echo second"
