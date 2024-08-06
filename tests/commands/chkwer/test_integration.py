from sinol_make import configure_parsers
from sinol_make.commands.chkwer import Command
from tests import util
from tests.fixtures import *


def run(arguments=None):
    util.create_ins_outs(os.getcwd())
    if arguments is None:
        arguments = []
    parser = configure_parsers()
    args = parser.parse_args(["chkwer"] + arguments)
    command = Command()
    command.run(args)


@pytest.mark.parametrize("create_package", [util.get_checker_package_path()], indirect=True)
def test_simple(create_package):
    """
    Test `chkwer` command withouth any arguments.
    """
    run()


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_no_checker(create_package, capsys):
    """
    The command should fail because there is no checker.
    """
    with pytest.raises(SystemExit):
        run()
    out = capsys.readouterr().out
    assert "Checker not found." in out


@pytest.mark.parametrize("create_package", [util.get_checker_package_path()], indirect=True)
def test_broken_model_solution(create_package, capsys):
    """
    The command should fail because the model solution doesn't receive max points.
    """
    os.unlink(os.path.join(os.getcwd(), "prog", "chk.cpp"))
    os.rename(os.path.join(os.getcwd(), "prog", "chk2.cpp"), os.path.join(os.getcwd(), "prog", "chk.cpp"))
    with pytest.raises(SystemExit):
        run()
    out = capsys.readouterr().out
    assert "Model solution didn't score maximum points." in out
