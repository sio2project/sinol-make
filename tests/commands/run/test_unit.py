import argparse, re, yaml

from sinol_make import util, oiejq
from sinol_make.structs.status_structs import Status, ResultChange, ValidationResult
from sinol_make.helpers import package_util
from .util import *
from ...util import *
from ...fixtures import *


def test_get_output_file():
    os.chdir(get_simple_package_path())
    command = get_command()
    assert command.get_output_file("in/abc1a.in") == "out/abc1a.out"


def test_compile_solutions(create_package):
    package_path = create_package
    command = get_command(package_path)
    solutions = package_util.get_solutions("abc", None)
    result = command.compile_solutions(solutions)
    assert result == [True for _ in solutions]


def test_execution(create_package, time_tool):
    package_path = create_package
    command = get_command(package_path)
    command.args.time_tool = time_tool
    command.timetool_name = time_tool
    solution = "abc.cpp"
    executable = package_util.get_executable(solution)
    result = command.compile_solutions([solution])
    assert result == [True]

    create_ins_outs(package_path)
    test = package_util.get_tests("abc", None)[0]

    with open(os.path.join(package_path, "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    os.makedirs(paths.get_executions_path(solution), exist_ok=True)
    result = command.run_solution((solution, paths.get_executables_path(executable), test, config['time_limit'], config['memory_limit'], oiejq.get_oiejq_path()))
    assert result.Status == Status.OK


def test_run_solutions(create_package, time_tool):
    package_path = create_package
    command = get_command(package_path)
    command.args = argparse.Namespace(solutions_report=False, time_tool=time_tool, compile_mode='default',
                                      hide_memory=False)
    create_ins_outs(package_path)
    command.tests = package_util.get_tests("abc", None)
    command.test_md5sums = {os.path.basename(test): util.get_file_md5(test) for test in command.tests}
    command.groups = list(sorted(set([command.get_group(test) for test in command.tests])))
    command.scores = command.config["scores"]
    command.possible_score = command.get_possible_score(command.groups)
    command.memory_limit = command.config["memory_limit"]
    command.time_limit = command.config["time_limit"]
    command.timetool_path = oiejq.get_oiejq_path()
    command.timetool_name = time_tool
    def flatten_results(results):
        new_results = {}
        for solution in results.keys():
            new_results[solution] = dict((group, group_result["status"])
                                         for group, group_result in results[solution].items())
        return new_results

    assert flatten_results(command.compile_and_run(["abc.cpp"])[0]) == {"abc.cpp": {1: Status.OK, 2: Status.OK, 3: Status.OK, 4: Status.OK}}
    assert flatten_results(command.compile_and_run(["abc.cpp", "abc4.cpp"])[0]) == {
        "abc.cpp": {1: Status.OK, 2: Status.OK, 3: Status.OK, 4: Status.OK},
        "abc4.cpp": {1: Status.OK, 2: Status.OK, 3: "WA", 4: "RE"}
    }


def test_validate_expected_scores_success():
    os.chdir(get_simple_package_path())
    command = get_command()
    command.scores = command.config["scores"]
    command.tests = ["in/abc1a.in", "in/abc2a.in", "in/abc3a.in", "in/abc4a.in"]
    command.groups = command.get_groups(command.tests)
    command.possible_score = command.contest.get_possible_score(command.groups, command.scores)

    # Test with correct expected scores.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=None, print_expected_scores=True)
    results = {
        "abc.cpp": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25}, 3: {"status": "OK", "points": 25}, 4: {"status": "OK", "points": 25}},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores == results.new_expected_scores
    assert results.removed_solutions == set()

    # Test with incorrect result.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=None, print_expected_scores=True)
    results = {
        "abc.cpp": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25}, 3: {"status": "OK", "points": 25}, 4: {"status": "WA", "points": 0}},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores != results.new_expected_scores
    assert len(results.changes) == 3

    # Test with removed solution.
    command.args = argparse.Namespace(solutions=None, tests=None, print_expected_scores=True)
    results = {
        "abc.cpp": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25}, 3: {"status": "OK", "points": 25}, 4: {"status": "OK", "points": 25}},
        "abc1.cpp": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25}, 3: {"status": "OK", "points": 25}, 4: {"status": "WA", "points": 0}},
        "abc2.cpp": {1: {"status": "OK", "points": 25}, 2: {"status": "WA", "points": 0}, 3: {"status": "WA", "points": 0}, 4: {"status": "TL", "points": 0}},
        "abc3.cpp": {1: {"status": "OK", "points": 25}, 2: {"status": "WA", "points": 0}, 3: {"status": "WA", "points": 0}, 4: {"status": "ML", "points": 0}},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores != results.new_expected_scores
    assert len(results.removed_solutions) == 1

    # Test with added solution and added group.
    command.config["scores"][5] = 0
    command.args = argparse.Namespace(solutions=["prog/abc.cpp", "prog/abc5.cpp"], tests=None,
                                      print_expected_scores=True)
    results = {
        "abc.cpp": {1: {"status": "OK", "points": 20}, 2: {"status": "OK", "points": 20}, 3: {"status": "OK", "points": 20}, 4: {"status": "OK", "points": 20}, 5: {"status": "WA", "points": 0}},
        "abc5.cpp": {1: {"status": "OK", "points": 20}, 2: {"status": "OK", "points": 20}, 3: {"status": "OK", "points": 20}, 4: {"status": "OK", "points": 20}, 5: {"status": "WA", "points": 0}},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores != results.new_expected_scores
    assert len(results.added_solutions) == 1
    assert len(results.added_groups) == 1

    # Test with removed group.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=None, print_expected_scores=True)
    results = {
        "abc.cpp": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25}, 3: {"status": "OK", "points": 25}},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores != results.new_expected_scores
    assert len(results.removed_groups) == 1

    # Test with correct expected scores and --tests flag.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=["in/abc1a.in", "in/abc2a.in"],
                                      print_expected_scores=True)
    results = {
        "abc.cpp": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25}},
    }
    results = command.validate_expected_scores(results)
    assert results.expected_scores == results.new_expected_scores


def test_validate_expected_scores_fail(capsys):
    os.chdir(get_simple_package_path())
    command = get_command()
    command.scores = {1: 20, 2: 20, 3: 20, 4: 20}

    # Test with missing points for group in config.
    command.args = argparse.Namespace(solutions=["prog/abc.cpp"], tests=None)
    results = {
        "abc.cpp": {1: {"status": "OK", "points": 20}, 2: {"status": "OK", "points": 20}, 3: {"status": "OK", "points": 20}, 4: {"status": "OK", "points": 20}, 5: {"status": "OK", "points": 20}},
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
    command.possible_score = 100

    # Test with correct expected scores.
    results = ValidationResult(
        added_solutions=set(),
        removed_solutions=set(),
        added_groups=set(),
        removed_groups=set(),
        changes=[],
        expected_scores={
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        new_expected_scores={
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        unknown_change=False,
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
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        new_expected_scores={
            "abc.cpp": {1: {"status": "WA", "points": 0}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        unknown_change=False,
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
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        new_expected_scores={
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
            "abc5.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        unknown_change=False,
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
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
            "abc5.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        new_expected_scores={
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        unknown_change=False,
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
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        new_expected_scores={
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100},
                        5: {"status": "OK", "points": 100}},
        },
        unknown_change=False,
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
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100},
                        5: {"status": "OK", "points": 100}},
        },
        new_expected_scores={
            "abc.cpp": {1: {"status": "OK", "points": 100}, 2: {"status": "OK", "points": 100},
                        3: {"status": "OK", "points": 100}, 4: {"status": "OK", "points": 100}},
        },
        unknown_change=False,
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
                "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25},
                             3: {"status": "OK", "points": 25}, 4: {"status": "OK", "points": 25}},
                "points": 100
            },
            "abc4.cpp": {
                "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25},
                             3: {"status": "OK", "points": 25}, 4: {"status": "OK", "points": 25}},
                "points": 100
            }
        },
        new_expected_scores={
            "abc.cpp": {
                "expected": {1: {"status": "WA", "points": 0}, 2: {"status": "OK", "points": 25},
                             3: {"status": "OK", "points": 25}, 5: {"status": "OK", "points": 0}},
                "points": 50
            },
            "abc5.cpp": {
                "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25},
                             3: {"status": "OK", "points": 25}, 5: {"status": "OK", "points": 0}},
                "points": 75
            }
        },
        unknown_change=False,
    )
    command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert "Saved suggested expected scores description." in out
    assert re.search(r"Solutions were added:.*abc5\.cpp", out) is not None
    assert re.search(r"Solutions were removed:.*abc4\.cpp", out) is not None
    assert re.search(r"Groups were added:.*5", out) is not None
    assert re.search(r"Groups were removed:.*4", out) is not None
    assert "Solution abc.cpp passed group 1 with status WA while it should pass with status OK." in out

    with open(os.path.join(package_path, "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    assert config["sinol_expected_scores"] == {
        "abc.cpp": {
            "expected": {1: {"status": "WA", "points": 0}, 2: {"status": "OK", "points": 25},
                         3: {"status": "OK", "points": 25}, 5: {"status": "OK", "points": 0}},
            "points": 50
        },
        "abc1.cpp": {
            "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25},
                         3: {"status": "OK", "points": 25}},
            "points": 75
        },
        "abc2.cpp": {
            "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "WA", "points": 0},
                         3: {"status": "WA", "points": 0}},
            "points": 25
        },
        "abc3.cpp": {
            "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "WA", "points": 0},
                         3: {"status": "WA", "points": 0}},
            "points": 25
        },
        "abc5.cpp": {
            "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25},
                         3: {"status": "OK", "points": 25}, 5: {"status": "OK", "points": 0}},
            "points": 75
        }
    }

    # Test with `unknown_changes = True`
    command.args = argparse.Namespace(apply_suggestions=False)
    results = ValidationResult(
        added_solutions=set(),
        removed_solutions=set(),
        added_groups=set(),
        removed_groups=set(),
        changes=[],
        expected_scores={
            "abc.cpp": {
                "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25},
                             3: {"status": "OK", "points": 25}, 4: {"status": "OK", "points": 25}},
                "points": 100
            },
        },
        new_expected_scores={
            "abc.cpp": {
                "expected": {1: {"status": "OK", "points": 25}, 2: {"status": "OK", "points": 25},
                             3: {"status": "OK", "points": 25}, 4: {"status": "OK", "points": 25}},
                "points": 100
            },
        },
        unknown_change=True,
    )
    with pytest.raises(SystemExit) as e:
        command.print_expected_scores_diff(results)
    out = capsys.readouterr().out
    assert e.type == SystemExit
    assert e.value.code == 1
    assert "There was an unknown change in expected scores." in out



@pytest.mark.parametrize("create_package", [get_simple_package_path()], indirect=True)
def test_set_scores(create_package):
    """
    Test set_scores function.
    """
    package_path = create_package
    command = get_command(package_path)
    command.tests = ["in/abc0a.in", "in/abc1a.in", "in/abc2a.in", "in/abc3a.in", "in/abc4a.in",
                     "in/abc5a.in", "in/abc6a.in"]
    del command.config["scores"]
    command.set_scores()
    assert command.scores == {
        0: 0,
        1: 16,
        2: 16,
        3: 16,
        4: 16,
        5: 16,
        6: 20
    }


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path()], indirect=True)
def test_get_valid_input_files(create_package):
    """
    Test get_valid_input_files function.
    """
    package_path = create_package
    command = get_command(package_path)
    create_ins_outs(package_path)
    command.tests = package_util.get_tests(command.ID, None)

    outputs = glob.glob(os.path.join(package_path, "out", "*.out"))
    os.unlink(outputs[0])
    valid_inputs = command.get_valid_input_files()
    assert len(valid_inputs) == len(outputs) - 1
    assert "in/" + os.path.basename(outputs[0].replace(".out", ".in")) not in valid_inputs
    assert "in/" + os.path.basename(outputs[1].replace(".out", ".in")) in valid_inputs


def test_update_group_status():
    from sinol_make.commands.run import update_group_status
    assert update_group_status(Status.OK, Status.WA) == Status.WA
    assert update_group_status(Status.PENDING, Status.OK) == Status.OK
    assert update_group_status(Status.PENDING, Status.WA) == Status.WA
    assert update_group_status(Status.WA, Status.CE) == Status.CE
    assert update_group_status(Status.CE, Status.WA) == Status.CE
