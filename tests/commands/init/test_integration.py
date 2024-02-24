import os
import pytest

from sinol_make import configure_parsers
from sinol_make.commands.init import Command
from tests.fixtures import temp_workdir


@pytest.mark.parametrize("temp_workdir", [''], indirect=True)
def test_simple(capsys, temp_workdir):
    """
    Test `init` command.
    """
    parser = configure_parsers()
    args = parser.parse_args(["init", "xyz"])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert 'Successfully created task "xyz"' in out

    # Check presence of some files:
    expected_files = ['config.yml', 'prog/xyz.cpp', 'prog/oi.h']

    for file in expected_files:
        assert os.path.isfile(os.path.join(os.getcwd(), file))
        
    # Check if task id is correctly set
    with open(os.path.join(os.getcwd(), 'config.yml')) as config_file:
        config_file_data = config_file.read()
        assert "sinol_task_id: xyz" in config_file_data
        assert "sinol_task_id: abc" not in config_file_data
