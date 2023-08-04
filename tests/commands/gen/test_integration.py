import sys

import yaml
import glob

from sinol_make import configure_parsers
from sinol_make.commands.gen import Command
from tests.fixtures import *
from tests import util


def simple_run():
    parser = configure_parsers()
    args = parser.parse_args(["gen"])
    command = Command()
    command.run(args)


def get_md5_sums(package_path):
    try:
        with open(os.path.join(package_path, "in", ".md5sums"), "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError | yaml.YAMLError:
        return {}


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(),
                                            util.get_simple_package_path()], indirect=True)
def test_simple(capsys, create_package):
    """
    Test `ingen` command with no parameters on package with no tests.
    """
    simple_run()

    out = capsys.readouterr().out
    assert "Successfully generated input files." in out
    assert "Successfully generated all output files." in out


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(),
                                            util.get_simple_package_path()], indirect=True)
def test_correct_inputs(capsys, create_package):
    """
    Test `ingen` command with all unchanged inputs.
    """
    simple_run()
    md5_sums = get_md5_sums(create_package)

    # Run again to check if all inputs are unchanged.
    simple_run()
    out = capsys.readouterr().out
    assert "All output files are up to date." in out
    assert md5_sums == get_md5_sums(create_package)


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(),
                                            util.get_simple_package_path()], indirect=True)
def test_changed_inputs(capsys, create_package):
    """
    Test `ingen` command with changed inputs.
    """
    simple_run()
    md5_sums = get_md5_sums(create_package)
    correct_md5 = md5_sums.copy()

    # Simulate change in input files.
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    for file in ins[:2]:
        md5_sums[os.path.basename(file)] = "0"

    with open(os.path.join(create_package, "in", ".md5sums"), "w") as f:
        yaml.dump(md5_sums, f)
    sys.stdout.write(str(md5_sums))

    simple_run()
    out = capsys.readouterr().out
    assert "Generating output files for 2 tests" in out
    for file in ins[:2]:
        assert "Successfully generated output file " + os.path.basename(file.replace("in", "out")) in out
    assert "Successfully generated all output files." in out
    assert correct_md5 == get_md5_sums(create_package)
