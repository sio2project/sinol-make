import time
import copy
import yaml
import glob

from sinol_make.commands.run import Command
from sinol_make.helpers import cache, package_util, paths
from sinol_make.structs.cache_structs import CacheFile
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest
from tests.fixtures import *
from tests import util


def run(package_path, arguments = None, time_tool = None, create_ins_outs = True):
    if arguments is None:
        arguments = ["run", "--time-tool", time_tool]
    if create_ins_outs:
        util.create_ins_outs(package_path)
    return util.run(Command, arguments)


def get_command():
    command: Command = util.get_run_command()
    command.base_run(None)
    return command


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_verify_status_package_path(),
                                            util.get_checker_package_path(), util.get_library_package_path(),
                                            util.get_library_string_args_package_path(), util.get_limits_package_path(),
                                            util.get_override_limits_package_path(), util.get_icpc_package_path(),
                                            util.get_long_solution_names_package(),
                                            util.get_large_output_package_path()],
                         indirect=True)
def test_simple(create_package, time_tool):
    """
    Test a simple run.
    """
    package_path = create_package
    with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    expected_scores = config["sinol_expected_scores"]
    run(package_path, time_tool=time_tool)

    with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    assert config["sinol_expected_scores"] == expected_scores


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_verify_status_package_path(),
                                            util.get_checker_package_path(), util.get_library_package_path(),
                                            util.get_library_string_args_package_path(), util.get_limits_package_path(),
                                            util.get_override_limits_package_path(), util.get_icpc_package_path(),
                                            util.get_long_solution_names_package()],
                         indirect=True)
def test_wrong_solution(create_package, time_tool):
    """
    Test if running after changing solution works.
    """
    package_path = create_package

    # First run to create cache.
    run(package_path, time_tool=time_tool)

    # Change solution.
    task_id = package_util.get_task_id()
    with open(os.path.join(os.path.join(package_path, "prog", f"{task_id}.cpp")), "w") as f:
        f.write("int main() { return 0; }")

    # Second run.
    with pytest.raises(SystemExit) as e:
        run(package_path, time_tool=time_tool, create_ins_outs=False)
    assert e.type == SystemExit
    assert e.value.code == 1


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_verify_status_package_path(),
                                            util.get_checker_package_path(), util.get_library_package_path(),
                                            util.get_library_string_args_package_path(), util.get_limits_package_path(),
                                            util.get_override_limits_package_path(), util.get_icpc_package_path(),
                                            util.get_large_output_package_path()],
                         indirect=True)
def test_no_expected_scores(capsys, create_package, time_tool):
    """
    Test with no sinol_expected_scores in config.yml.
    Should run, but exit with exit code 1.
    Checks if a message about added solutions is printed.
    """
    package_path = create_package
    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    del config["sinol_expected_scores"]
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    with pytest.raises(SystemExit) as e:
        run(package_path, time_tool=time_tool)

    assert e.type == SystemExit
    assert e.value.code == 1

    out = capsys.readouterr().out
    assert "Solutions were added:" in out
    assert "There was an unknown change in expected scores." not in out
    command = get_command()
    solution = command.get_correct_solution()
    assert solution.basename in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_verify_status_package_path(),
                                            util.get_checker_package_path(), util.get_library_package_path(),
                                            util.get_library_string_args_package_path(), util.get_limits_package_path(),
                                            util.get_override_limits_package_path(), util.get_icpc_package_path(),
                                            util.get_long_solution_names_package(),
                                            util.get_large_output_package_path()],
                         indirect=True)
def test_apply_suggestions(create_package, time_tool, capsys):
    """
    Test with no sinol_expected_scores in config.yml.
    Verifies that suggestions are applied.
    Checks if the genereated config.yml is correct.
    """
    package_path = create_package

    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    expected_scores = config["sinol_expected_scores"]
    del config["sinol_expected_scores"]
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    run(package_path, ["run", "--apply-suggestions", "--time-tool", time_tool])

    out = capsys.readouterr().out
    assert "There was an unknown change in expected scores." not in out
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
    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    config["sinol_expected_scores"]["abc.cpp"]["expected"][1] = {"status": "WA", "points": 0}
    config["sinol_expected_scores"]["abc.cpp"]["points"] = 75
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    with pytest.raises(SystemExit) as e:
        run(package_path, time_tool=time_tool)

    out = capsys.readouterr().out

    assert e.type == SystemExit
    assert e.value.code == 1
    assert "Solution abc.cpp passed group 1 with status OK while it should pass with status WA." in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_checker_package_path(),
                                            util.get_library_package_path(),
                                            util.get_library_string_args_package_path(),
                                            util.get_icpc_package_path(), util.get_long_solution_names_package()],
                         indirect=True)
def test_flag_tests(create_package, time_tool):
    """
    Test flag --tests.
    Checks if correct tests are run.
    """
    package_path = create_package
    util.create_ins_outs(package_path)
    task_id = package_util.get_task_id()
    test = InputTest.get_all(task_id)[0]
    command = run(package_path, ["run", "--tests", test.basename, "--time-tool", time_tool],
                  create_ins_outs=False)

    assert len(command.tests) == 1
    assert command.tests[0] == test


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_verify_status_package_path(),
                                            util.get_checker_package_path(), util.get_icpc_package_path()],
                         indirect=True)
def test_flag_solutions(capsys, create_package, time_tool):
    """
    Test flag --solutions.
    Checks if correct solutions are run (by checking the output).
    """
    package_path = create_package
    util.create_ins_outs(package_path)

    command = get_command()
    solutions = command.get_all_solutions()
    run(package_path, ["run", "--solutions", solutions[0].basename, "--time-tool", time_tool])

    out = capsys.readouterr().out

    assert os.path.basename(solutions[0].basename) in out
    assert os.path.basename(solutions[1].basename) not in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_verify_status_package_path(),
                                            util.get_checker_package_path()], indirect=True)
def test_flag_solutions_multiple(capsys, create_package, time_tool):
    """
    Test flag --solutions with multiple solutions.
    """
    package_path = create_package

    command = get_command()
    solutions = command.get_all_solutions()
    run(package_path, ["run", "--solutions", solutions[0].basename, os.path.join("prog", solutions[1].basename),
                       "--time-tool", time_tool])

    out = capsys.readouterr().out

    assert os.path.basename(solutions[0].basename) in out
    assert os.path.basename(solutions[1].basename) in out
    assert os.path.basename(solutions[2].basename) not in out


@pytest.mark.parametrize("create_package", [util.get_weak_compilation_flags_package_path()], indirect=True)
def test_weak_compilation_flags(create_package, time_tool):
    """
    Test flag --weak-compilation-flags.
    """
    package_path = create_package
    with pytest.raises(SystemExit) as e:
        run(package_path, time_tool=time_tool, create_ins_outs=False)

    assert e.type == SystemExit
    assert e.value.code == 1

    run(package_path, ["run", "--weak-compilation-flags", "--time-tool", time_tool],
        create_ins_outs=False)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_no_scores(capsys, create_package, time_tool):
    """
    Test with no scores key in config.yml.
    """
    package_path = create_package

    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    del config["scores"]
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    run(package_path, time_tool=time_tool)
    out = capsys.readouterr().out
    assert "Scores are not defined in config.yml. Points will be assigned equally to all groups." in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_verify_status_package_path()],
                         indirect=True)
def test_missing_output_files(capsys, create_package):
    """
    Test with missing output files.
    """
    package_path = create_package
    util.create_ins_outs(package_path)
    command = get_command()
    task_id = package_util.get_task_id()
    outs = OutputTest.get_all(task_id)
    outs[0].remove()
    outs[1].remove()
    in1 = command.get_corresponding_test(outs[0])
    in2 = command.get_corresponding_test(outs[1])
    with pytest.raises(SystemExit):
        run(package_path, time_tool="time", create_ins_outs=False)
    out = capsys.readouterr().out
    assert f'Missing output files for tests: {in1.basename}, {in2.basename}' in out


@pytest.mark.parametrize("create_package", [util.get_limits_package_path()], indirect=True)
def test_no_limits_in_config(capsys, create_package, time_tool):
    """
    Test with missing `time_limits` and `memory_limits` keys in config.yml.
    """
    package_path = create_package
    config_path = os.path.join(package_path, "config.yml")
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    del config["time_limits"]
    del config["memory_limits"]
    with open(config_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    with pytest.raises(SystemExit):
        run(package_path, time_tool=time_tool)

    out = capsys.readouterr().out
    assert "Solution lim2.cpp passed group 1 with status TL while it should pass with status OK." in out
    assert "Solution lim4.cpp passed group 2 with status ML while it should pass with status OK." in out
    assert "Use flag --apply-suggestions to apply suggestions." in out


@pytest.mark.parametrize("create_package", [util.get_limits_package_path()], indirect=True)
def test_time_limit_flag(capsys, create_package, time_tool):
    """
    Test flag --tl.
    """
    package_path = create_package
    with pytest.raises(SystemExit):
        run(package_path, ["run", "--tl", "20", "--time-tool", time_tool])

    out = capsys.readouterr().out
    assert "Solution lim2.cpp passed group 2 with status OK while it should pass with status TL." in out


@pytest.mark.parametrize("create_package", [util.get_limits_package_path()], indirect=True)
def test_memory_limit_flag(capsys, create_package, time_tool):
    """
    Test flag --ml.
    """
    package_path = create_package
    with pytest.raises(SystemExit):
        run(package_path, ["run", "--ml", "256", "--time-tool", time_tool])

    out = capsys.readouterr().out
    assert "Solution lim3.cpp passed group 1 with status OK while it should pass with status ML." in out
    assert "Solution lim4.cpp passed group 1 with status OK while it should pass with status ML." in out


@pytest.mark.parametrize("create_package", [util.get_override_limits_package_path()], indirect=True)
def test_override_limits(create_package, time_tool):
    """
    Test `override_limits` key in config.yml.
    """
    package_path = create_package
    config_file_path = os.path.join(package_path, "config.yml")

    # With `override_limits` key deleted.
    with open(config_file_path, "r") as config_file:
        original_config = yaml.load(config_file, Loader=yaml.SafeLoader)
    config = copy.deepcopy(original_config)
    del config["override_limits"]
    with open(config_file_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    run(package_path, ["run", "--apply-suggestions", "--time-tool", time_tool])
    with open(config_file_path, "r") as config:
        config = yaml.load(config, Loader=yaml.SafeLoader)

    assert config["sinol_expected_scores"] == {
        "ovl.cpp": {
            "expected": {1: {"status": "TL", "points": 0}, 2: {"status": "TL", "points": 0}},
            "points": 0
        }
    }

    # With global `time_limit` deleted, `memory_limit` in `override_limits` deleted
    # and global `memory_limit` set to 256.
    config = copy.deepcopy(original_config)
    del config["time_limit"]
    del config["override_limits"]['cpp']["memory_limit"]
    config["memory_limit"] = 256
    with open(config_file_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    run(package_path, ["run", "--apply-suggestions", "--time-tool", time_tool])
    with open(config_file_path, "r") as config:
        config = yaml.load(config, Loader=yaml.SafeLoader)

    assert config["sinol_expected_scores"] == {
        "ovl.cpp": {
            "expected": {1: {"status": "ML", "points": 0}, 2: {"status": "ML", "points": 0}},
            "points": 0
        }
    }


@pytest.mark.parametrize("create_package", [util.get_stack_size_package_path()], indirect=True)
def test_mem_limit_kill(create_package, time_tool):
    """
    Test if `sinol-make` kills solution if it runs with memory limit exceeded.
    """
    package_path = create_package
    start_time = time.time()
    with pytest.raises(SystemExit) as e:
        run(package_path, time_tool=time_tool, create_ins_outs=False)
    end_time = time.time()

    assert e.value.code == 1
    assert end_time - start_time < 10  # The solution runs for 20 seconds, but it immediately exceeds memory limit,
                                       # so it should be killed.


@pytest.mark.parametrize("create_package", [util.get_undocumented_options_package_path()], indirect=True)
def test_undocumented_time_tool_option(create_package):
    """
    Test if `undocumented_time_tool` option works.
    """
    package_path = create_package
    command = run(package_path, ["run"])
    assert command.timetool_manager.used_timetool.get_name() == "time"


@pytest.mark.oiejq
@pytest.mark.parametrize("create_package", [util.get_undocumented_options_package_path()], indirect=True)
def test_override_undocumented_time_tool_option(create_package):
    """
    Test if overriding `undocumented_time_tool` option with --time-tool flag works.
    """
    package_path = create_package
    command = run(package_path, ["run", "--time-tool", "sio2jail"])
    assert command.timetool_manager.used_timetool.get_name() == "sio2jail"


@pytest.mark.parametrize("create_package", [util.get_undocumented_options_package_path()], indirect=True)
def test_undocumented_test_limits_option(create_package, capsys):
    """
    Test if `undocumented_test_limits` option works.
    """
    package_path = create_package
    run(package_path, ["run"])

    with open(os.path.join(os.getcwd(), "config.yml")) as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    del config["sinol_undocumented_test_limits"]
    with open(os.path.join(os.getcwd(), "config.yml"), "w") as config_file:
        config_file.write(yaml.dump(config))

    with pytest.raises(SystemExit) as e:
        run(package_path, ["run"])

    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "und1a.in: Specifying limit for a single test is not allowed in sinol-make." in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_example_tests_package_path()],
                         indirect=True)
def test_no_tests(create_package, time_tool, capsys):
    """
    Test if `sinol-make` doesn't crash when there are no tests to run.
    """
    with pytest.raises(SystemExit) as e:
        run(create_package, time_tool=time_tool, create_ins_outs=False)
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "There are no tests to run." in out


@pytest.mark.parametrize("create_package", [util.get_example_tests_package_path()], indirect=True)
def test_only_example_tests(create_package, time_tool, capsys):
    """
    Test if `sinol-make` works only on example tests
    """
    package_path = create_package
    run(package_path, time_tool=time_tool)
    out = capsys.readouterr().out
    assert "Expected scores are correct!" in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_checker_package_path(),
                                            util.get_library_package_path()], indirect=True)
def test_flag_tests_not_existing_tests(create_package, time_tool, capsys):
    """
    Test flag --tests with not existing tests.
    """
    package_path = create_package
    with pytest.raises(SystemExit) as e:
        run(package_path, ["run", "--tests", "in/non_existing_file", "--time-tool", time_tool])
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "There are no tests to run." in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_verify_status_package_path(),
                                            util.get_checker_package_path(), util.get_library_package_path(),
                                            util.get_library_string_args_package_path(), util.get_limits_package_path(),
                                            util.get_override_limits_package_path(),
                                            util.get_long_solution_names_package()],
                         indirect=True)
def test_results_caching(create_package, time_tool):
    """
    Test if test results are cached.
    """
    package_path = create_package

    start_time = time.time()
    run(package_path, time_tool=time_tool)
    length = time.time() - start_time

    start_time = time.time()
    command = run(package_path, time_tool=time_tool)
    end_time = time.time() - start_time
    assert end_time - start_time < length / 2

    solutions = command.get_all_solutions()
    for solution in solutions:
        cache_file: CacheFile = cache.get_cache_file(solution.file_path)
        for test in command.tests:
            assert test.md5 in cache_file.tests
            test_cache = cache_file.tests[test.md5]
            lang = solution.lang
            assert test_cache.time_limit == package_util.get_time_limit(test, command.config, lang, command.task_id)
            assert test_cache.memory_limit == package_util.get_memory_limit(test, command.config, lang, command.task_id)
        assert cache_file is not None
        assert cache_file.tests != {}


@pytest.mark.parametrize("create_package", [util.get_checker_package_path()], indirect=True)
def test_results_caching_checker_changed(create_package, time_tool):
    """
    Test if after changing checker source code, all cached test results are removed.
    """
    package_path = create_package

    # First run to cache test results.
    command = run(package_path, time_tool=time_tool)

    # Change checker source code.
    checker_source = ""
    with open(os.path.join(os.getcwd(), "prog", "chkchk.cpp"), "r") as f:
        checker_source = f.read()
    with open(os.path.join(os.getcwd(), "prog", "chkchk.cpp"), "w") as f:
        f.write("// Changed checker source code.\n" + checker_source)

    # Compile checker check if test results are removed.
    checker = command.get_checker()
    exe, _ = checker.compile()
    assert exe is not None
    solutions = command.get_all_solutions()
    assert len(solutions) > 0
    for solution in solutions:
        cache_file: CacheFile = cache.get_cache_file(solution.file_path)
        assert cache_file.tests == {}


@pytest.mark.parametrize("create_package", [util.get_library_package_path()], indirect=True)
def test_extra_compilation_files_change(create_package, time_tool):
    """
    Test if after changing extra compilation files, all cached test results are removed.
    """
    package_path = create_package
    def change_file(file, comment_character):
        with open(file, "r") as f:
            source = f.read()
        with open(file, "w") as f:
            f.write(f"{comment_character} Changed source code.\n" + source)

    def test(file_to_change, lang, comment_character):
        # First run to cache test results.
        command = run(package_path, time_tool=time_tool)

        # Change file
        change_file(os.path.join(os.getcwd(), "prog", file_to_change), comment_character)

        cache.save_to_cache_extra_compilation_files(command.config.get("extra_compilation_files", []), command.task_id)
        solutions = command.get_all_solutions()
        for solution in solutions:
            if solution.lang == lang:
                assert not os.path.exists(paths.get_cache_path("md5sums", solution.basename))
                info = cache.get_cache_file(solution.file_path)
                assert info == CacheFile()

    test("liblib.cpp", "cpp", "//")
    test("liblib.h", "cpp", "//")
    test("liblib.py", "py", "#")


@pytest.mark.parametrize("create_package", [get_simple_package_path()], indirect=True)
def test_contest_type_change(create_package, time_tool):
    """
    Test if after changing contest type, all cached test results are removed.
    """
    package_path = create_package

    # First run to cache test results.
    run(package_path, time_tool=time_tool)

    # Change contest type.
    config_path = os.path.join(os.getcwd(), "config.yml")
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    config["sinol_contest_type"] = "oi"
    with open(config_path, "w") as f:
        f.write(yaml.dump(config))

    # Compile checker check if test results are removed.
    # We remove tests, so that `run()` exits before creating new cached test results.
    for test in glob.glob("in/*.in"):
        os.unlink(test)
    with pytest.raises(SystemExit):
        run(package_path, time_tool=time_tool, create_ins_outs=False)

    command = get_command()
    solutions = command.get_all_solutions()
    for solution in solutions:
        cache_file: CacheFile = cache.get_cache_file(solution.file_path)
        assert cache_file.tests == {}


@pytest.mark.parametrize("create_package", [get_simple_package_path()], indirect=True)
def test_cwd_in_prog(create_package):
    """
    Test if `sinol-make` works when cwd is in prog.
    """
    package_path = create_package
    os.chdir("prog")
    run(package_path, ["run", "--time-tool", "time"])
