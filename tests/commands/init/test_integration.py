import os
import pytest

from sinol_make import configure_parsers
from sinol_make.commands.init import Command
from tests.fixtures import temp_workdir


@pytest.mark.parametrize("temp_workdir", [''], indirect=True)
def test_init_clones_default_template(capsys, request, temp_workdir):
    """
    Test `init` command.
    """
    parser = configure_parsers()
    args = ["init", "xyz"]

    # try to avoid connecting to github when cloning example_package
    rootdir = str(request.config.rootdir)
    git_dir = os.path.join(rootdir, '.git')
    if os.path.exists(git_dir):
        git_local_url = os.path.join('file://', rootdir)
        args.extend(["-t", git_local_url, "example_package"])
    else:
        # copy from root directory instead of cloning
        # if needed we could take a dependency on gitpython and mock up a repo
        args.extend(["-t", rootdir, "example_package"])

    args = parser.parse_args(args)
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
