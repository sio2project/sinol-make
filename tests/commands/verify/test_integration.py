import os
import sys

import pytest

from sinol_make import configure_parsers
from sinol_make.commands.verify import Command
from tests import util
from tests.fixtures import create_package


def run(args=None):
    if args is None:
        args = []
    parser = configure_parsers()
    command = Command()
    args = parser.parse_args(['verify'] + args)
    command.run(args)


@pytest.mark.parametrize("create_package", [util.get_stresstest_package_path()], indirect=True)
def test_stresstest_package(capsys, create_package):
    """
    Test if stresstest.sh script runs. Then check if after failing the stresstest.sh script, the verify command
    will fail as well.
    """
    run()
    out = capsys.readouterr().out
    assert "Running stress tests" in out
    assert "Very hard stress test" in out

    code = ""
    stresstest_path = os.path.join(create_package, "prog", "strstresstest.sh")
    with open(stresstest_path, "r") as f:
        code = f.read()
    with open(stresstest_path, "w") as f:
        f.write(code.replace("exit 0", "exit 1"))

    with pytest.raises(SystemExit) as e:
        run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    err = capsys.readouterr().err
    sys.stdout.write(err)
    assert "Running stress tests" in out
    assert "Very hard stress test" in out
    assert "Stress tests failed." in out
