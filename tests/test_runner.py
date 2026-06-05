from unittest.mock import MagicMock, patch

from command_book.models import Command, Param
from command_book.runner import ask_params, execute, resolve


def test_resolve_no_params():
    assert resolve("ls -la", [], {}) == "ls -la"


def test_resolve_required_param():
    params = [Param(name="host")]
    values = {"host": "192.168.1.1"}
    result = resolve("ssh {{host}}", params, values)
    assert result == "ssh 192.168.1.1"


def test_resolve_with_default_provided():
    params = [Param(name="port", default="22")]
    values = {"port": "2222"}
    result = resolve("ssh server -p {{port::22}}", params, values)
    assert result == "ssh server -p 2222"


def test_resolve_with_default_fallback():
    params = [Param(name="port", default="22")]
    values = {}
    result = resolve("ssh server -p {{port::22}}", params, values)
    assert result == "ssh server -p 22"


def test_resolve_multiple_params():
    params = [
        Param(name="user", default="root"),
        Param(name="host"),
        Param(name="port", default="22"),
        ]
    values = {"host": "10.0.0.1"}
    result = resolve(
        "ssh {{user::root}}@{{host}} -p {{port::22}}", params, values)
    assert result == "ssh root@10.0.0.1 -p 22"


def test_resolve_overrides_default():
    params = [Param(name="user", default="root")]
    values = {"user": "admin"}
    result = resolve("ssh {{user::root}}@server", params, values)
    assert result == "ssh admin@server"


def test_execute_returns_exit_code():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        assert execute("echo hi") == 0
        mock_run.assert_called_once_with("echo hi", shell=True)


def test_execute_returns_nonzero():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        assert execute("false") == 1


def test_ask_params_required():
    cmd = Command(key="test", cmd="ssh {{host}!}")
    text_mock = MagicMock()
    text_mock.return_value.execute.side_effect = ["", "localhost"]
    with patch("command_book.runner.inquirer.text", text_mock):
        values = ask_params(cmd)
    assert values == {"host": "localhost"}


def test_ask_params_optional_empty_uses_default():
    cmd = Command(key="test", cmd="ssh -p {{port::22}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = ""
    with patch("command_book.runner.inquirer.text", text_mock):
        values = ask_params(cmd)
    assert values == {"port": "22"}


def test_ask_params_optional_with_value():
    cmd = Command(key="test", cmd="ssh -p {{port::22}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "2222"
    with patch("command_book.runner.inquirer.text", text_mock):
        values = ask_params(cmd)
    assert values == {"port": "2222"}


def test_ask_params_no_params():
    cmd = Command(key="test", cmd="ssh {{host}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "myserver"
    with patch("command_book.runner.inquirer.text", text_mock):
        values = ask_params(cmd)
    assert values == {"host": "myserver"}
