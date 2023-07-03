from ...fixtures import *
from .util import *
from sinol_make import configure_parsers


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path()], indirect=True)
def test_simple(create_package, time_tool):
    """
    Test a simple run.
    """
    package_path = create_package
    create_ins_outs(package_path)

    parser = configure_parsers()

    args = parser.parse_args(["run", "--time_tool", time_tool])
    command = Command()
    command.run(args)


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path()], indirect=True)
def test_no_expected_scores(capsys, create_package, time_tool):
    """
    Test with no sinol_expected_scores in config.yml.
    Should run, but exit with exit code 1.
    Checks if a message about added solutions is printed.
    """
    package_path = create_package
    create_ins_outs(package_path)

    config_path = os.path.join(package_path, "config.yml")
    config = yaml.load(open(config_path, "r"), Loader=yaml.SafeLoader)
    del config["sinol_expected_scores"]
    open(config_path, "w").write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time_tool", time_tool])
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
                                            get_checker_package_path()], indirect=True)
def test_apply_suggestions(create_package, time_tool):
    """
    Test with no sinol_expected_scores in config.yml.
    Verifies that suggestions are applied.
    Checks if the genereated config.yml is correct.
    """
    package_path = create_package
    create_ins_outs(package_path)

    config_path = os.path.join(package_path, "config.yml")
    config = yaml.load(open(config_path, "r"), Loader=yaml.SafeLoader)
    expected_scores = config["sinol_expected_scores"]
    del config["sinol_expected_scores"]
    open(config_path, "w").write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--apply_suggestions", "--time_tool", time_tool])
    command = Command()
    command.run(args)

    config = yaml.load(open(config_path, "r"), Loader=yaml.SafeLoader)
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
    config = yaml.load(open(config_path, "r"), Loader=yaml.SafeLoader)
    config["sinol_expected_scores"]["abc.cpp"]["expected"][1] = "WA"
    config["sinol_expected_scores"]["abc.cpp"]["points"] = 75
    open(config_path, "w").write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time_tool", time_tool])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    out = capsys.readouterr().out

    assert e.type == SystemExit
    assert e.value.code == 1
    assert "Solution abc.cpp passed group 1 with status OK while it should pass with status WA." in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_checker_package_path()], indirect=True)
def test_flag_tests(create_package, time_tool):
    """
    Test flag --tests.
    Checks if correct tests are run.
    """
    package_path = create_package
    create_ins_outs(package_path)

    test = glob.glob(os.path.join(package_path, "in", "???*.in"))[0]
    parser = configure_parsers()
    args = parser.parse_args(["run", "--tests", test, "--time_tool", time_tool])
    command = Command()
    command.run(args)

    assert command.tests == [test]


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
    args = parser.parse_args(["run", "--solutions", solutions[0], "--time_tool", time_tool])
    command = Command()
    command.run(args)

    out = capsys.readouterr().out

    assert os.path.basename(solutions[0]) in out
    assert os.path.basename(solutions[1]) not in out
