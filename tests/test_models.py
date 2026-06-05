from command_book.models import Command, Param


def test_command_params_no_defaults():
    cmd = Command(key="test", cmd="ssh {{user}}@{{host}}")
    params = cmd.params()
    assert len(params) == 2
    assert params[0] == Param(name="user", default=None)
    assert params[1] == Param(name="host", default=None)


def test_command_params_with_defaults():
    cmd_text = "ssh {{user::root}}@{{host}} -p {{port::22}}"
    cmd = Command(key="test", cmd=cmd_text)
    params = cmd.params()
    assert params[0] == Param(name="user", default="root")
    assert params[1] == Param(name="host", default=None)
    assert params[2] == Param(name="port", default="22")


def test_command_params_required():
    cmd_text = "ssh {{user::root}!}@{{host}!} -p {{port::22}!}"
    cmd = Command(key="test", cmd=cmd_text)
    params = cmd.params()
    assert params[0] == Param(name="user", default="root", required=True)
    assert params[1] == Param(name="host", default=None, required=True)
    assert params[2] == Param(name="port", default="22", required=True)


def test_command_params_empty():
    cmd = Command(key="test", cmd="ls -la")
    assert cmd.params() == []
