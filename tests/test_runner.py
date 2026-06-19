import os
from unittest.mock import MagicMock, patch

from command_book.models import Command, Param, ParamType
from command_book.runner import _ask_params, _execute, _resolve


def test_resolve_no_params():
    assert _resolve("ls -la", [], {}) == "ls -la"


def test_resolve_required_param():
    params = [Param(name="host")]
    values = {"host": "192.168.1.1"}
    result = _resolve("ssh {{host}}", params, values)
    assert result == "ssh 192.168.1.1"


def test_resolve_with_default_provided():
    params = [Param(name="port", default="22")]
    values = {"port": "2222"}
    result = _resolve("ssh server -p {{port::22}}", params, values)
    assert result == "ssh server -p 2222"


def test_resolve_with_default_fallback():
    params = [Param(name="port", default="22")]
    values = {}
    result = _resolve("ssh server -p {{port::22}}", params, values)
    assert result == "ssh server -p 22"


def test_resolve_multiple_params():
    params = [
        Param(name="user", default="root"),
        Param(name="host"),
        Param(name="port", default="22"),
        ]
    values = {"host": "10.0.0.1"}
    result = _resolve(
        "ssh {{user::root}}@{{host}} -p {{port::22}}", params, values)
    assert result == "ssh root@10.0.0.1 -p 22"


def test_resolve_overrides_default():
    params = [Param(name="user", default="root")]
    values = {"user": "admin"}
    result = _resolve("ssh {{user::root}}@server", params, values)
    assert result == "ssh admin@server"


def test_resolve_escaped_not_replaced():
    params = []
    result = _resolve(r"echo \{{not_a_param}} hello", params, {})
    assert result == "echo {{not_a_param}} hello"


def test_resolve_type_path():
    params = [Param(name="file", type=ParamType.PATH)]
    values = {"file": "/etc/hosts"}
    result = _resolve("cat {{file}path}", params, values)
    assert result == "cat /etc/hosts"


def test_resolve_type_int():
    params = [Param(name="port", type=ParamType.INT, default="22")]
    values = {"port": "8080"}
    result = _resolve("nc host {{port::22}int}", params, values)
    assert result == "nc host 8080"


def test_execute_returns_exit_code():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        assert _execute("echo hi") == 0
        executable = os.environ.get("SHELL", "/bin/sh") or None
        mock_run.assert_called_once_with(
            "echo hi", shell=True, executable=executable)


def test_execute_returns_nonzero():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        assert _execute("false") == 1


def test_ask_params_required():
    cmd = Command(key="test", cmd="ssh {{host}!}")
    text_mock = MagicMock()
    text_mock.return_value.execute.side_effect = ["", "localhost"]
    with patch("command_book.runner.inquirer.text", text_mock):
        values = _ask_params(cmd.params)
    assert values == {"host": "localhost"}


def test_ask_params_optional_empty_not_uses_default():
    cmd = Command(key="test", cmd="ssh -p {{port::22}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = ""
    with patch("command_book.runner.inquirer.text", text_mock):
        values = _ask_params(cmd.params)
    assert values == {"port": ""}


def test_ask_params_optional_with_value():
    cmd = Command(key="test", cmd="ssh -p {{port::22}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "2222"
    with patch("command_book.runner.inquirer.text", text_mock):
        values = _ask_params(cmd.params)
    assert values == {"port": "2222"}


def test_ask_params_no_params():
    cmd = Command(key="test", cmd="ssh {{host}}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "myserver"
    with patch("command_book.runner.inquirer.text", text_mock):
        values = _ask_params(cmd.params)
    assert values == {"host": "myserver"}


def test_ask_params_text_multiline():
    cmd = Command(key="test", cmd="echo {{msg}text}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "line1\nline2\n"
    with patch("command_book.runner.inquirer.text", text_mock):
        values = _ask_params(cmd.params)
    assert values == {"msg": "line1\nline2"}
    _, kwargs = text_mock.call_args
    assert kwargs["multiline"] is True


def test_ask_params_path():
    cmd = Command(key="test", cmd="cat {{file}path}")
    filepath_mock = MagicMock()
    filepath_mock.return_value.execute.return_value = "/etc/hosts"
    with patch("command_book.runner.inquirer.filepath", filepath_mock):
        values = _ask_params(cmd.params)
    assert values == {"file": "/etc/hosts"}


def test_ask_params_int_valid():
    cmd = Command(key="test", cmd="nc host {{port}int}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "8080"
    with patch("command_book.runner.inquirer.text", text_mock):
        values = _ask_params(cmd.params)
    assert values == {"port": "8080"}


def test_ask_params_int_uses_text_widget():
    cmd = Command(key="test", cmd="nc host {{port}int}")
    text_mock = MagicMock()
    text_mock.return_value.execute.return_value = "22"
    with patch("command_book.runner.inquirer.text", text_mock):
        _ask_params(cmd.params)
    text_mock.assert_called_once()
    _, kwargs = text_mock.call_args
    assert "validate" in kwargs


def test_ask_params_required_path():
    cmd = Command(key="test", cmd="cat {{file}path!}")
    filepath_mock = MagicMock()
    filepath_mock.return_value.execute.side_effect = ["", "/etc/hosts"]
    with patch("command_book.runner.inquirer.filepath", filepath_mock):
        values = _ask_params(cmd.params)
    assert values == {"file": "/etc/hosts"}


def test_ask_params_select():
    cmd = Command(key="test", cmd="deploy {{env}select:dev,staging,prod}")
    select_mock = MagicMock()
    select_mock.return_value.execute.return_value = "staging"
    with patch("command_book.runner.inquirer.select", select_mock):
        values = _ask_params(cmd.params)
    assert values == {"env": "staging"}
    _, kwargs = select_mock.call_args
    assert kwargs["choices"] == ["dev", "staging", "prod"]
