import argparse, re, yaml
from sinol_make import util
from sinol_make.commands.run.structs import ResultChange, ValidationResult
from .util import *
from ...util import *
from ...fixtures import *

def test_extract_test_no():
    os.chdir(get_simple_package_path())
    command = get_command()
    assert command.extract_test_no("in/abc1a.in") == "1a"


def test_extract_file_name():
    os.chdir(get_simple_package_path())
    command = get_command()
    assert command.extract_file_name("in/abc1a.in") == "abc1a.in"


def test_get_group():
    os.chdir(get_simple_package_path())
    command = get_command()
    assert command.get_group("in/abc1a.in") == 1


def test_get_output_file():
    os.chdir(get_simple_package_path())
    command = get_command()
    assert command.get_output_file("in/abc1a.in") == "out/abc1a.out"


def test_get_solutions():
    os.chdir(get_simple_package_path())
    command = get_command()

    solutions = command.get_solutions(None)
    assert solutions == ["abc.cpp", "abc1.cpp", "abc2.cpp", "abc3.cpp", "abc4.cpp"]
    solutions = command.get_solutions(["prog/abc.cpp"])
    assert solutions == ["abc.cpp"]
    assert "abc1.cpp" not in solutions


def test_get_executable_key():
    os.chdir(get_simple_package_path())
    command = get_command()
    assert command.get_executable_key("abc1.e") == (0, 1)


def test_get_executable():
    os.chdir(get_simple_package_path())
    command = get_command()
    assert command.get_executable("abc.cpp") == "abc.e"


def test_compile_solutions(create_package):
    package_path = create_package
    command = get_command(package_path)
    solutions = command.get_solutions(None)
    result = command.compile_solutions(solutions)
    assert result == [True for _ in solutions]


def test_get_tests(create_package):
    package_path = create_package
    command = get_command(package_path)
    create_ins(package_path, command)
    os.chdir(package_path)
    tests = command.get_tests(None)
    assert tests == ["in/abc1a.in", "in/abc2a.in", "in/abc3a.in", "in/abc4a.in"]


def test_execution(create_package, time_tool):
    package_path = create_package
    command = get_command(package_path)
    command.args = argparse.Namespace(time_tool=time_tool, weak_compilation_flags=False)
    solution = "abc.cpp"
    executable = command.get_executable(solution)
    result = command.compile_solutions([solution])
    assert result == [True]

    create_ins(package_path, command)
    os.chdir(package_path)
    create_outs(package_path, command)
    os.chdir(package_path)
    test = command.get_tests(None)[0]

    config = yaml.load(open(os.path.join(package_path, "config.yml"), "r"), Loader=yaml.FullLoader)

    os.makedirs(os.path.join(command.EXECUTIONS_DIR, solution), exist_ok=True)
    result = command.run_solution((solution, os.path.join(command.EXECUTABLES_DIR, executable), test, config['time_limit'], config['memory_limit'], util.get_oiejq_path()))
    assert result.Status == "OK"


def test_calculate_points():
    os.chdir(get_simple_package_path())
    command = get_command()

    assert command.calculate_points({1: "OK", 2: "OK", 3: "OK", 4: "OK"}) == 100
    assert command.calculate_points({1: "OK", 2: "OK", 3: "OK", 4: "WA"}) == 75
    assert command.calculate_points({1: "OK", 2: "OK", 3: "TL"}) == 50
    assert command.calculate_points({1: "OK"}) == 25
    assert command.calculate_points({1: "WA"}) == 0


def test_run_solutions(create_package, time_tool):
    package_path = create_package
    command = get_command(package_path)
    command.args = argparse.Namespace(solutions_report=False, time_tool=time_tool, weak_compilation_flags=False)
    create_ins_outs(package_path, command)
    command.tests = command.get_tests(None)
    command.groups = list(sorted(set([command.get_group(test) for test in command.tests])))
    command.scores = command.config["scores"]
    command.possible_score = command.get_possible_score(command.groups)
    command.memory_limit = command.config["memory_limit"]
    command.time_limit = command.config["time_limit"]
    command.timetool_path = util.get_oiejq_path()

    print(command.compile_and_run(["abc.cpp"]))
    assert command.compile_and_run(["abc.cpp"]) == {"abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"}}
    assert command.compile_and_run(["abc.cpp", "abc4.cpp"]) == {
        "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        "abc4.cpp": {1: "OK", 2: "OK", 3: "WA", 4: "RE"}
    }


def test_print_expected_scores(capsys):
    os.chdir(get_simple_package_path())
    command = get_command()
    expected_scores = """sinol_expected_scores:
  abc.cpp:
    expected: {1: "OK", 2: "OK", 3: "OK", 4: "OK"}
    points: 100
  abc1.cpp:
    expected: {1: "OK", 2: "OK", 3: "OK", 4: "WA"}
    points: 75
  abc2.cpp:
    expected: {1: "OK", 2: "WA", 3: "WA", 4: "TL"}
    points: 25
  abc3.cpp:
    expected: {1: "OK", 2: "WA", 3: "WA", 4: "ML"}
    points: 25
  abc4.cpp:
    expected: {1: "OK", 2: "OK", 3: "WA", 4: "RE"}
    points: 50

"""

    expected_scores_dict = yaml.load(expected_scores, Loader=yaml.FullLoader)
    command.print_expected_scores(expected_scores_dict["sinol_expected_scores"])
    out = capsys.readouterr().out
    assert out == expected_scores.replace('"', '')


def test_validate_expected_scores_success():
    command = get_command()
    os.chdir(get_simple_package_path())
    command.scores = command.config["scores"]

    # Test with correct expected scores.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=None)
    results = {
        "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores == results.new_expected_scores
    assert results.removed_solutions == set()

    # Test with incorrect result.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=None)
    results = {
        "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "WA"},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores != results.new_expected_scores
    assert len(results.changes) == 1

    # Test with removed solution.
    command.args = argparse.Namespace(solutions=None, tests=None)
    results = {
        "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        "abc1.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "WA"},
        "abc2.cpp": {1: "OK", 2: "WA", 3: "WA", 4: "TL"},
        "abc3.cpp": {1: "OK", 2: "WA", 3: "WA", 4: "ML"},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores != results.new_expected_scores
    assert len(results.removed_solutions) == 1

    # Test with added solution and added group.
    command.config["scores"][5] = 0
    command.args = argparse.Namespace(solutions=["prog/abc.cpp", "prog/abc5.cpp"], tests=None)
    results = {
        "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK", 5: "WA"},
        "abc5.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK", 5: "WA"},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores != results.new_expected_scores
    assert len(results.added_solutions) == 1
    assert len(results.added_groups) == 1

    # Test with removed group.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=None)
    results = {
        "abc.cpp": {1: "OK", 2: "OK", 3: "OK"},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores != results.new_expected_scores
    assert len(results.removed_groups) == 1

    # Test with correct expected scores and --tests flag.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=["in/abc1a.in", "in/abc2a.in"])
    results = {
        "abc.cpp": {1: "OK", 2: "OK"},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores == results.new_expected_scores


def test_validate_expected_scores_fail(capsys):
    command = get_command()
    os.chdir(get_simple_package_path())
    command.scores = command.config["scores"]

    # Test with missing points for group in config.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=None)
    results = {
        "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK", 5: "OK"},
    }
    with pytest.raises(SystemExit) as e:
        command.validate_expected_scores(results)

    assert e.type == SystemExit
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Group 5 doesn't have points specified in config file." in out


def test_print_expected_scores_diff(capsys, create_package):
    package_path = create_package
    command = get_command(package_path)
    command.args = argparse.Namespace(apply_suggestions=False)

    # Test with correct expected scores.
    results = ValidationResult(
        added_solutions=set(),
        removed_solutions=set(),
        added_groups=set(),
        removed_groups=set(),
        changes=[],
        expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        },
        new_expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        }
    )
    command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert "Expected scores are correct!" in out

    # Test with one incorrect group result.
    results = ValidationResult(
        added_solutions=set(),
        removed_solutions=set(),
        added_groups=set(),
        removed_groups=set(),
        changes=[ResultChange("abc.cpp", 1, "OK", "WA")],
        expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        },
        new_expected_scores={
            "abc.cpp": {1: "WA", 2: "OK", 3: "OK", 4: "OK"},
        }
    )
    with pytest.raises(SystemExit) as e:
        command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert e.type == SystemExit
    assert e.value.code == 1
    assert "Solution abc.cpp passed group 1 with status WA while it should pass with status OK." in out

    # Test with added solution.
    results = ValidationResult(
        added_solutions={"abc5.cpp"},
        removed_solutions=set(),
        added_groups=set(),
        removed_groups=set(),
        changes=[],
        expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        },
        new_expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
            "abc5.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        }
    )
    with pytest.raises(SystemExit) as e:
        command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert e.type == SystemExit
    assert e.value.code == 1
    assert re.search(r"Solutions were added:.*abc5\.cpp", out) is not None

    # Test with removed solution.
    results = ValidationResult(
        added_solutions=set(),
        removed_solutions={"abc5.cpp"},
        added_groups=set(),
        removed_groups=set(),
        changes=[],
        expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
            "abc5.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        },
        new_expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        }
    )
    with pytest.raises(SystemExit) as e:
        command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert e.type == SystemExit
    assert e.value.code == 1
    assert re.search(r"Solutions were removed:.*abc5\.cpp", out) is not None

    # Test with added group.
    results = ValidationResult(
        added_solutions=set(),
        removed_solutions=set(),
        added_groups={5},
        removed_groups=set(),
        changes=[],
        expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        },
        new_expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK", 5: "OK"},
        }
    )
    with pytest.raises(SystemExit) as e:
        command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert e.type == SystemExit
    assert e.value.code == 1
    assert re.search(r"Groups were added:.*5", out) is not None

    # Test with removed group.
    results = ValidationResult(
        added_solutions=set(),
        removed_solutions=set(),
        added_groups=set(),
        removed_groups={5},
        changes=[],
        expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK", 5: "OK"},
        },
        new_expected_scores={
            "abc.cpp": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
        }
    )
    with pytest.raises(SystemExit) as e:
        command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert e.type == SystemExit
    assert e.value.code == 1
    assert re.search(r"Groups were removed:.*5", out) is not None

    # Test with --apply_suggestions flag set.
    command.args = argparse.Namespace(apply_suggestions=True)
    command.scores = command.config["scores"]
    command.scores[5] = 0
    results = ValidationResult(
        added_solutions={"abc5.cpp"},
        removed_solutions={"abc4.cpp"},
        added_groups={5},
        removed_groups={4},
        changes=[ResultChange("abc.cpp", 1, "OK", "WA")],
        expected_scores={
            "abc.cpp": {
                "expected": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
                "points": 100
            },
            "abc4.cpp": {
                "expected": {1: "OK", 2: "OK", 3: "OK", 4: "OK"},
                "points": 100
            }
        },
        new_expected_scores={
            "abc.cpp": {
                "expected": {1: "WA", 2: "OK", 3: "OK", 5: "OK"},
                "points": 50
            },
            "abc5.cpp": {
                "expected": {1: "OK", 2: "OK", 3: "OK", 5: "OK"},
                "points": 75
            }
        }
    )
    command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert "Saved suggested expected scores description." in out
    assert re.search(r"Solutions were added:.*abc5\.cpp", out) is not None
    assert re.search(r"Solutions were removed:.*abc4\.cpp", out) is not None
    assert re.search(r"Groups were added:.*5", out) is not None
    assert re.search(r"Groups were removed:.*4", out) is not None
    assert "Solution abc.cpp passed group 1 with status WA while it should pass with status OK." in out

    config = yaml.load(open(os.path.join(package_path, "config.yml"), "r"), Loader=yaml.FullLoader)
    assert config["sinol_expected_scores"] == {
        "abc.cpp": {
            "expected": {1: "WA", 2: "OK", 3: "OK", 5: "OK"},
            "points": 50
        },
        "abc1.cpp": {
            "expected": {1: "OK", 2: "OK", 3: "OK"},
            "points": 75
        },
        "abc2.cpp": {
            "expected": {1: "OK", 2: "WA", 3: "WA"},
            "points": 25
        },
        "abc3.cpp": {
            "expected": {1: "OK", 2: "WA", 3: "WA"},
            "points": 25
        },
        "abc5.cpp": {
            "expected": {1: "OK", 2: "OK", 3: "OK", 5: "OK"},
            "points": 75
        }
    }
