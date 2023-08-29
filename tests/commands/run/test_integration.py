import copy
import sys
import pytest

from ...fixtures import *
from .util import *
from sinol_make import configure_parsers


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_library_package_path(),
                                            get_library_string_args_package_path(), get_limits_package_path()],
                         indirect=True)
def test_simple(create_package, time_tool):
    """
    Test a simple run.
    """
    package_path = create_package
    create_ins_outs(package_path)

    parser = configure_parsers()

    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    command.run(args)


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_library_package_path(),
                                            get_library_string_args_package_path(), get_limits_package_path()],
                         indirect=True)
def test_no_expected_scores(capsys, create_package, time_tool):
    """
    Test with no sinol_expected_scores in config.yml.
    Should run, but exit with exit code 1.
    Checks if a message about added solutions is printed.
    """
    package_path = create_package
    create_ins_outs(package_path)

    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    del config["sinol_expected_scores"]
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 1

    out = capsys.readouterr().out
    assert "Solutions were added:" in out
    solution = glob.glob(os.path.join(package_path, "prog", "???.*"))[0]
    assert os.path.basename(solution) in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_library_package_path(),
                                            get_library_string_args_package_path(), get_limits_package_path()],
                         indirect=True)
def test_apply_suggestions(create_package, time_tool):
    """
    Test with no sinol_expected_scores in config.yml.
    Verifies that suggestions are applied.
    Checks if the genereated config.yml is correct.
    """
    package_path = create_package
    create_ins_outs(package_path)

    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    expected_scores = config["sinol_expected_scores"]
    del config["sinol_expected_scores"]
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--apply-suggestions", "--time-tool", time_tool])
    command = Command()
    command.run(args)

    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    assert config["sinol_expected_scores"] == expected_scores


def test_incorrect_expected_scores(capsys, create_package, time_tool):
    """
    Test with incorrect sinol_expected_scores in config.yml.
    Should exit with exit code 1.
    Checks if a message about incorrect result is printed.
    """
    package_path = create_package
    create_ins_outs(package_path)

    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    config["sinol_expected_scores"]["abc.cpp"]["expected"][1] = "WA"
    config["sinol_expected_scores"]["abc.cpp"]["points"] = 75
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    out = capsys.readouterr().out

    assert e.type == SystemExit
    assert e.value.code == 1
    assert "Solution abc.cpp passed group 1 with status OK while it should pass with status WA." in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_checker_package_path(),
                                            get_library_package_path(), get_library_string_args_package_path()],
                         indirect=True)
def test_flag_tests(create_package, time_tool):
    """
    Test flag --tests.
    Checks if correct tests are run.
    """
    package_path = create_package
    create_ins_outs(package_path)

    test = glob.glob(os.path.join(package_path, "in", "???*.in"))[0]
    parser = configure_parsers()
    args = parser.parse_args(["run", "--tests", test, "--time-tool", time_tool])
    command = Command()
    try:
        command.run(args)
    except SystemExit:
        pass

    assert command.tests == [test]


@pytest.mark.parametrize("create_package", [get_checker_package_path()], indirect=True)
def test_groups_in_flag_test(capsys, create_package, time_tool):
    """
    Test flag --tests with whole and partial groups.
    """
    package_path = create_package
    create_ins_outs(package_path)

    parser = configure_parsers()

    # Test with only one test from group 1.
    args = parser.parse_args(["run", "--tests", "in/chk1a.in", "--time-tool", time_tool])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert "Showing expected scores only for groups with all tests run." in out
    assert "sinol_expected_scores: {}" in out
    assert "Expected scores are correct!" in out

    # Test with all tests from group 1.
    args = parser.parse_args(["run", "--tests", "in/chk1a.in", "in/chk1b.in", "in/chk1c.in", "--time-tool", time_tool])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert 'sinol_expected_scores:\n' \
           '  chk.cpp:\n' \
           '    expected: {1: OK}\n' \
           '    points: 50\n' \
           '  chk1.cpp:\n' \
           '    expected: {1: WA}\n' \
           '    points: 0\n' \
           '  chk2.cpp:\n' \
           '    expected:\n' \
           '      1: {points: 25, status: OK}\n' \
           '    points: 25\n' \
           '  chk3.cpp:\n' \
           '    expected: {1: OK}\n' \
           '    points: 50' in out

    # Test with incorrect expected scores for first group.
    with open(os.path.join(package_path, "config.yml"), "r") as config_file:
        correct_config = yaml.load(config_file, Loader=yaml.SafeLoader)
    config = copy.deepcopy(correct_config)
    config["sinol_expected_scores"]["chk.cpp"]["expected"][1] = "WA"
    config["sinol_expected_scores"]["chk.cpp"]["points"] = 50
    with open(os.path.join(package_path, "config.yml"), "w") as config_file:
        config_file.write(yaml.dump(config))

    args = parser.parse_args(["run", "--tests", "in/chk1a.in", "in/chk1b.in", "in/chk1c.in", "--time-tool", time_tool,
                              "--apply-suggestions"])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    sys.stdout.write(out)
    assert "Solution chk.cpp passed group 1 with status OK while it should pass with status WA." in out
    with open(os.path.join(package_path, "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    assert config == correct_config


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path()], indirect=True)
def test_flag_solutions(capsys, create_package, time_tool):
    """
    Test flag --solutions.
    Checks if correct solutions are run (by checking the output).
    """
    package_path = create_package
    create_ins_outs(package_path)

    solutions = glob.glob(os.path.join(package_path, "prog", "????.*"))
    parser = configure_parsers()
    args = parser.parse_args(["run", "--solutions", solutions[0], "--time-tool", time_tool])
    command = Command()
    command.run(args)

    out = capsys.readouterr().out

    assert os.path.basename(solutions[0]) in out
    assert os.path.basename(solutions[1]) not in out


@pytest.mark.parametrize("create_package", [get_weak_compilation_flags_package_path()], indirect=True)
def test_weak_compilation_flags(create_package):
    """
    Test flag --weak-compilation-flags.
    """
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", "time"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 1

    args = parser.parse_args(["run", "--weak-compilation-flags", "--time-tool", "time"])
    command = Command()
    command.run(args)


@pytest.mark.parametrize("create_package", [get_simple_package_path()], indirect=True)
def test_no_scores(capsys, create_package, time_tool):
    """
    Test with no scores key in config.yml.
    """
    package_path = create_package
    command = get_command()
    create_ins_outs(package_path)

    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    del config["scores"]
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    command.run(args)

    out = capsys.readouterr().out
    assert "Scores are not defined in config.yml. Points will be assigned equally to all groups." in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path()], indirect=True)
def test_missing_output_files(capsys, create_package):
    """
    Test with missing output files.
    """
    package_path = create_package
    command = get_command()
    create_ins_outs(package_path)

    outs = glob.glob(os.path.join(package_path, "out", "*.out"))
    outs.sort()
    os.unlink(outs[0])
    os.unlink(outs[1])
    out1 = command.extract_file_name(outs[0]).replace(".out", ".in")
    out2 = command.extract_file_name(outs[1]).replace(".out", ".in")

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", "time"])
    command = Command()
    with pytest.raises(SystemExit):
        command.run(args)

    out = capsys.readouterr().out
    assert f'Missing output files for tests: {out1}, {out2}' in out


@pytest.mark.parametrize("create_package", [get_limits_package_path()], indirect=True)
def test_no_limits_in_config(capsys, create_package, time_tool):
    """
    Test with missing `time_limits` and `memory_limits` keys in config.yml.
    """
    package_path = create_package
    command = get_command()
    create_ins_outs(package_path)

    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    del config["time_limits"]
    del config["memory_limits"]
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    with pytest.raises(SystemExit):
        command.run(args)

    out = capsys.readouterr().out
    assert "Use flag --apply-suggestions to apply suggestions." in out


@pytest.mark.parametrize("create_package", [get_limits_package_path()], indirect=True)
def test_time_limit_flag(capsys, create_package, time_tool):
    """
    Test flag --tl.
    """
    package_path = create_package
    command = get_command()
    create_ins_outs(package_path)

    parser = configure_parsers()
    args = parser.parse_args(["run", "--tl", "20", "--time-tool", time_tool])
    command = Command()
    with pytest.raises(SystemExit):
        command.run(args)

    out = capsys.readouterr().out
    assert "Solution lim1.cpp passed group 1 with status OK while it should pass with status TL." in out
    assert "Solution lim2.cpp passed group 1 with status OK while it should pass with status TL." in out
    assert "Solution lim2.cpp passed group 2 with status OK while it should pass with status TL." in out


@pytest.mark.parametrize("create_package", [get_limits_package_path()], indirect=True)
def test_memory_limit_flag(capsys, create_package, time_tool):
    """
    Test flag --ml.
    """
    package_path = create_package
    command = get_command()
    create_ins_outs(package_path)

    parser = configure_parsers()
    args = parser.parse_args(["run", "--ml", "256", "--time-tool", time_tool])
    command = Command()
    with pytest.raises(SystemExit):
        command.run(args)

    out = capsys.readouterr().out
    assert "Solution lim3.cpp passed group 1 with status OK while it should pass with status ML." in out
    assert "Solution lim4.cpp passed group 1 with status OK while it should pass with status ML." in out
    assert "Solution lim4.cpp passed group 2 with status OK while it should pass with status ML." in out
