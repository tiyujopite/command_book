from unittest.mock import patch

from command_book.models import Param
from command_book.runner import execute, resolve


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
