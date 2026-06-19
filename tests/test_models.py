import pytest

from command_book.models import Command, Param, ParamType


def test_command_params_no_defaults():
    cmd_ = "ssh {{user}}@{{host}}"
    cmd = Command(key="test", cmd=cmd_)
    assert len(cmd.params) == 2
    assert cmd.params[0] == Param(name="user")
    assert cmd.params[1] == Param(name="host")
    with pytest.raises(NotImplementedError):
        assert cmd.params[1] == "host"  # cover NotImplemented in __eq__


def test_command_params_with_defaults():
    cmd_ = "ssh {{user::root}}@{{host}} -p {{port::22}}"
    cmd = Command(key="test", cmd=cmd_)
    assert cmd.params[0] == Param(name="user", default="root")
    assert cmd.params[1] == Param(name="host")
    assert cmd.params[2] == Param(name="port", default="22")


def test_command_params_required():
    cmd_ = "ssh {{user::root}!}@{{host}!} -p {{port::22}!}"
    cmd = Command(key="test", cmd=cmd_)
    assert cmd.params[0] == Param(name="user", default="root", required=True)
    assert cmd.params[1] == Param(name="host", required=True)
    assert cmd.params[2] == Param(name="port", default="22", required=True)


def test_command_params_empty():
    cmd_ = "ls -la"
    cmd = Command(key="test", cmd=cmd_)
    assert cmd.params == []


def test_command_params_types():
    cmd_ = "cp {{src}path} {{dst}path} --port {{port}int}"
    cmd = Command(key="test", cmd=cmd_)
    assert cmd.params[0] == Param(name="src", type=ParamType.PATH)
    assert cmd.params[1] == Param(name="dst", type=ParamType.PATH)
    assert cmd.params[2] == Param(name="port", type=ParamType.INT)


def test_command_params_type_default_is_char():
    cmd_ = "echo {{text}}"
    cmd = Command(key="test", cmd=cmd_)
    assert cmd.params[0].type == ParamType.CHAR


def test_command_params_type_text():
    cmd_ = "echo {{body}text}"
    cmd = Command(key="test", cmd=cmd_)
    assert cmd.params[0] == Param(name="body", type=ParamType.TEXT)


def test_command_params_type_with_default_and_required():
    cmd_ = "cat {{file::/etc/hosts}path!}"
    cmd = Command(key="test", cmd=cmd_)
    param = Param(
        name="file", type=ParamType.PATH, default="/etc/hosts", required=True)
    assert cmd.params[0] == param


def test_command_params_duplicate_same():
    cmd_ = "echo {{text}} {{text}}"
    cmd = Command(key="test", cmd=cmd_)
    assert len(cmd.params) == 1


def test_command_params_duplicate_conflict_type():
    with pytest.raises(ValueError):
        cmd_ = "echo {{val}char} {{val}int}"
        Command(key="test", cmd=cmd_)


def test_command_params_duplicate_conflict_required():
    with pytest.raises(ValueError):
        cmd_ = "echo {{val}!} {{val}}"
        Command(key="test", cmd=cmd_)


def test_command_empty_key():
    with pytest.raises(ValueError):
        Command(key="", cmd="ls")


def test_command_empty_cmd():
    with pytest.raises(ValueError):
        Command(key="test", cmd="")


def test_command_params_escaped():
    cmd = Command(key="test", cmd=r"echo \{{not_a_param}} {{real}}")
    assert len(cmd.params) == 1
    assert cmd.params[0] == Param(name="real")


def test_command_params_escaped_complex():
    cmd = Command(key="test", cmd=r"echo \{{not_a_param::foo}int!} {{real}}")
    assert len(cmd.params) == 1
    assert cmd.params[0] == Param(name="real")


def test_command_params_escaped_only():
    cmd = Command(key="test", cmd=r"echo \{{not_a_param}}")
    assert cmd.params == []


def test_command_pretty_optional():
    cmd_ = "echo {{text}}"
    cmd = Command(key="test", cmd=cmd_)
    assert "[cyan]" in cmd.pretty()


def test_command_pretty_required():
    cmd_ = "echo {{text}!}"
    cmd = Command(key="test", cmd=cmd_)
    assert "[yellow]" in cmd.pretty()


def test_command_pretty_escaped_not_colored():
    cmd_ = r"echo \{{not_a_param}}"
    cmd = Command(key="test", cmd=cmd_)
    pretty = cmd.pretty()
    assert "[cyan]" not in pretty
    assert "[yellow]" not in pretty
    assert "{{not_a_param}}" in pretty


def test_command_param_with_espaces():
    cmd_ = r"echo {{val ue::default\ value}}"
    cmd = Command(key="test", cmd=cmd_)
    assert len(cmd.params) == 0


def test_param_required_name():
    with pytest.raises(ValueError):
        Param(name="", type=ParamType.CHAR)


def test_param_int_default_invalid():
    with pytest.raises(ValueError):
        Param(name="port", type=ParamType.INT, default="not_a_number")


def test_command_params_select():
    cmd = Command(key="test", cmd="deploy {{env}select:dev,staging,prod}")
    assert cmd.params[0] == Param(
        name="env", type=ParamType.SELECT, choices=["dev", "staging", "prod"])


def test_command_params_select_with_default():
    cmd = Command(key="test", cmd="deploy {{env::dev}select:dev,staging,prod}")
    assert cmd.params[0] == Param(name="env", type=ParamType.SELECT,
        default="dev", choices=["dev", "staging", "prod"])


def test_command_params_select_required():
    cmd = Command(key="test", cmd="deploy {{env}select:dev,staging,prod!}")
    assert cmd.params[0].required is True


def test_param_select_no_choices():
    with pytest.raises(ValueError):
        Param(name="env", type=ParamType.SELECT, choices=[])


def test_param_select_default_not_in_choices():
    with pytest.raises(ValueError):
        Param(name="env", type=ParamType.SELECT, default="qa",
            choices=["dev", "staging", "prod"])


def test_command_pretty_select():
    cmd = Command(key="test", cmd="deploy {{env}select:dev,staging,prod}")
    assert "[cyan]" in cmd.pretty()
    assert "select:dev,staging,prod" in cmd.pretty()


def test_command_params_select_duplicate_conflict_choices():
    with pytest.raises(ValueError):
        Command(key="test",
            cmd="x {{env}select:dev,prod} {{env}select:dev,staging,prod}")
