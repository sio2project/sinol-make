import copy
import sys
import time
import pytest
import copy

from sinol_make.helpers import cache
from sinol_make.structs.cache_structs import CacheFile
from ...fixtures import *
from .util import *
from sinol_make import configure_parsers, util, oiejq


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_library_package_path(),
                                            get_library_string_args_package_path(), get_limits_package_path(),
                                            get_override_limits_package_path(), get_icpc_package_path(),
                                            get_long_solution_names_package(), get_large_output_package_path()],
                         indirect=True)
def test_simple(create_package, time_tool):
    """
    Test a simple run.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()

    with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    expected_scores = config["sinol_expected_scores"]

    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    command.run(args)

    with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    assert config["sinol_expected_scores"] == expected_scores


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_library_package_path(),
                                            get_library_string_args_package_path(), get_limits_package_path(),
                                            get_override_limits_package_path(), get_icpc_package_path(),
                                            get_long_solution_names_package()],
                         indirect=True)
def test_wrong_solution(create_package, time_tool):
    """
    Test if running after changing solution works.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()

    # First run to create cache.
    command.run(args)

    # Change solution.
    task_id = package_util.get_task_id()
    with open(os.path.join(os.path.join(package_path, "prog", f"{task_id}.cpp")), "w") as f:
        f.write("int main() { return 0; }")

    # Second run.
    with pytest.raises(SystemExit) as e:
        command.run(args)
    assert e.type == SystemExit
    assert e.value.code == 1


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_library_package_path(),
                                            get_library_string_args_package_path(), get_limits_package_path(),
                                            get_override_limits_package_path(), get_icpc_package_path(),
                                            get_large_output_package_path()],
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
    assert "There was an unknown change in expected scores." not in out
    solution = package_util.get_files_matching_pattern(command.ID, f"{command.ID}.*")[0]
    assert os.path.basename(solution) in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_library_package_path(),
                                            get_library_string_args_package_path(), get_limits_package_path(),
                                            get_override_limits_package_path(), get_icpc_package_path(),
                                            get_long_solution_names_package(), get_large_output_package_path()],
                         indirect=True)
def test_apply_suggestions(create_package, time_tool, capsys):
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

    out = capsys.readouterr().out
    assert "There was an unknown change in expected scores."
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
    config["sinol_expected_scores"]["abc.cpp"]["expected"][1] = {"status": "WA", "points": 0}
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
                                            get_library_package_path(), get_library_string_args_package_path(),
                                            get_icpc_package_path(), get_long_solution_names_package()],
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

    assert command.tests == [os.path.join("in", os.path.basename(test))]


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_icpc_package_path()], indirect=True)
def test_flag_solutions(capsys, create_package, time_tool):
    """
    Test flag --solutions.
    Checks if correct solutions are run (by checking the output).
    """
    package_path = create_package
    create_ins_outs(package_path)

    task_id = package_util.get_task_id()
    solutions = package_util.get_files_matching_pattern(task_id, f'{task_id}?.*')
    parser = configure_parsers()
    args = parser.parse_args(["run", "--solutions", solutions[0], "--time-tool", time_tool])
    command = Command()
    command.run(args)

    out = capsys.readouterr().out

    assert os.path.basename(solutions[0]) in out
    assert os.path.basename(solutions[1]) not in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path()], indirect=True)
def test_flag_solutions_multiple(capsys, create_package, time_tool):
    """
    Test flag --solutions with multiple solutions.
    """
    package_path = create_package
    create_ins_outs(package_path)

    task_id = package_util.get_task_id()
    solutions = [
        os.path.basename(file)
        for file in package_util.get_files_matching_pattern(task_id, f'{task_id}?.*')
    ]
    parser = configure_parsers()
    args = parser.parse_args(["run", "--solutions", solutions[0], os.path.join("prog", solutions[1]),
                              "--time-tool", time_tool])
    command = Command()
    command.run(args)

    out = capsys.readouterr().out

    assert os.path.basename(solutions[0]) in out
    assert os.path.basename(solutions[1]) in out
    assert os.path.basename(solutions[2]) not in out


@pytest.mark.parametrize("create_package", [get_weak_compilation_flags_package_path()], indirect=True)
def test_weak_compilation_flags(create_package):
    """
    Test flag --compile-mode weak flag.
    """
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", "time"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 1

    args = parser.parse_args(["run", "--compile-mode", "weak", "--time-tool", "time"])
    command = Command()
    command.run(args)


@pytest.mark.parametrize("create_package", [get_oioioi_compilation_flags_package_path()], indirect=True)
def test_oioioi_compilation_flags(create_package):
    """
    Test flag --compile-mode oioioi flag.
    """
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", "time"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 1

    args = parser.parse_args(["run", "--compile-mode", "oioioi", "--time-tool", "time"])
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
    assert 'There are tests without outputs.' in out
    assert 'Run outgen to fix this issue or add the --no-outputs flag to ignore the issue.' in out
    assert 'An error occurred while running the command.' not in out
    
    
@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path()], indirect=True)
def test_missing_output_files_allow_missing(capsys, create_package):
    """
    Test with missing output files.
    """
    package_path = create_package
    command = get_command()
    create_ins_outs(package_path)

    outs = glob.glob(os.path.join(package_path, "out", "*.out"))
    for i in outs:
        os.unlink(i)

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", "time", "--no-outputs"])
    command = Command()
    with pytest.raises(SystemExit):
        command.run(args)

    out = capsys.readouterr().out
    assert 'No tests with valid outputs.' in out
    assert 'An error occurred while running the command.' not in out
    assert 'There are tests without outputs.' not in out
    assert 'Run outgen to fix this issue or add the --no-outputs flag to ignore the issue.' not in out


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
    assert "Solution lim2.cpp passed group 1 with status TL while it should pass with status OK." in out
    assert "Solution lim4.cpp passed group 2 with status ML while it should pass with status OK." in out
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


@pytest.mark.parametrize("create_package", [get_override_limits_package_path()], indirect=True)
def test_override_limits(create_package, time_tool):
    """
    Test `override_limits` key in config.yml.
    """
    package_path = create_package
    command = get_command()
    create_ins_outs(package_path)
    config_file_path = os.path.join(package_path, "config.yml")

    # With `override_limits` key deleted.
    with open(config_file_path, "r") as config_file:
        original_config = yaml.load(config_file, Loader=yaml.SafeLoader)
    config = copy.deepcopy(original_config)
    del config["override_limits"]
    with open(config_file_path, "w") as config_file:
        config_file.write(yaml.dump(config))

    parser = configure_parsers()
    args = parser.parse_args(["run", "--apply-suggestions", "--time-tool", time_tool])
    command = Command()
    command.run(args)
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

    command = Command()
    command.run(args)
    with open(config_file_path, "r") as config:
        config = yaml.load(config, Loader=yaml.SafeLoader)

    assert config["sinol_expected_scores"] == {
        "ovl.cpp": {
            "expected": {1: {"status": "ML", "points": 0}, 2: {"status": "ML", "points": 0}},
            "points": 0
        }
    }


@pytest.mark.parametrize("create_package", [get_stack_size_package_path()], indirect=True)
def test_mem_limit_kill(create_package, time_tool):
    """
    Test if `st-make` kills solution if it runs with memory limit exceeded.
    """
    package_path = create_package
    command = get_command()
    create_ins_outs(package_path)

    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    start_time = time.time()
    with pytest.raises(SystemExit) as e:
        command.run(args)
    end_time = time.time()

    assert e.value.code == 1
    assert end_time - start_time < 10  # The solution runs for 20 seconds, but it immediately exceeds memory limit,
                                       # so it should be killed.


@pytest.mark.parametrize("create_package", [get_undocumented_options_package_path()], indirect=True)
def test_undocumented_time_tool_option(create_package):
    """
    Test if `undocumented_time_tool` option works.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run"])
    command = Command()
    command.run(args)
    assert command.timetool_path == "time"


@pytest.mark.oiejq
@pytest.mark.parametrize("create_package", [get_undocumented_options_package_path()], indirect=True)
def test_override_undocumented_time_tool_option(create_package):
    """
    Test if overriding `undocumented_time_tool` option with --time-tool flag works.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", "oiejq"])
    command = Command()
    command.run(args)
    assert command.timetool_path == oiejq.get_oiejq_path()


@pytest.mark.parametrize("create_package", [get_undocumented_options_package_path()], indirect=True)
def test_undocumented_test_limits_option(create_package, capsys):
    """
    Test if `undocumented_test_limits` option works.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run"])
    command = Command()
    command.run(args)

    with open(os.path.join(os.getcwd(), "config.yml")) as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
    del config["sinol_undocumented_test_limits"]
    with open(os.path.join(os.getcwd(), "config.yml"), "w") as config_file:
        config_file.write(yaml.dump(config))

    command = Command()
    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "und1a.in: Specifying limit for a single test is not allowed in st-make." in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_example_tests_package_path()], indirect=True)
def test_no_tests(create_package, time_tool, capsys):
    """
    Test if `st-make` doesn't crash when there are no tests to run.
    """
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "There are no tests to run." in out


@pytest.mark.parametrize("create_package", [get_example_tests_package_path()], indirect=True)
def test_only_example_tests(create_package, time_tool, capsys):
    """
    Test if `st-make` works only on example tests
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert "Expected scores are correct!" in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_checker_package_path(),
                                            get_library_package_path()], indirect=True)
def test_flag_tests_not_existing_tests(create_package, time_tool, capsys):
    """
    Test flag --tests with not existing tests.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--tests", "in/non_existing_file", "--time-tool", time_tool])
    command = Command()
    with pytest.raises(SystemExit) as e:
        command.run(args)
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "There are no tests to run." in out


@pytest.mark.parametrize("create_package", [get_simple_package_path(), get_verify_status_package_path(),
                                            get_checker_package_path(), get_library_package_path(),
                                            get_library_string_args_package_path(), get_limits_package_path(),
                                            get_override_limits_package_path(), get_long_solution_names_package()],
                         indirect=True)
def test_results_caching(create_package, time_tool):
    """
    Test if test results are cached.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])

    def run():
        command = Command()
        command.run(args)
        return command

    start_time = time.time()
    run()
    length = time.time() - start_time

    start_time = time.time()
    command = run()
    end_time = time.time() - start_time
    assert end_time - start_time < length / 2

    task_id = package_util.get_task_id()
    solutions = package_util.get_solutions(task_id, None)
    for solution in solutions:
        cache_file: CacheFile = cache.get_cache_file(solution)
        for test in command.tests:
            assert util.get_file_md5(test) in cache_file.tests
            test_cache = cache_file.tests[util.get_file_md5(test)]
            lang = package_util.get_file_lang(solution)
            assert test_cache.time_limit == package_util.get_time_limit(test, command.config, lang, command.ID)
            assert test_cache.memory_limit == package_util.get_memory_limit(test, command.config, lang, command.ID)
        assert cache_file is not None
        assert cache_file.tests != {}


@pytest.mark.parametrize("create_package", [get_checker_package_path()], indirect=True)
def test_results_caching_checker_changed(create_package, time_tool):
    """
    Test if after changing checker source code, all cached test results are removed.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])

    # First run to cache test results.
    command = Command()
    command.run(args)

    # Change checker source code.
    checker_source = ""
    with open(os.path.join(os.getcwd(), "prog", "chkchk.cpp"), "r") as f:
        checker_source = f.read()
    with open(os.path.join(os.getcwd(), "prog", "chkchk.cpp"), "w") as f:
        f.write("// Changed checker source code.\n" + checker_source)

    # Compile checker check if test results are removed.
    command.compile_checker()
    task_id = package_util.get_task_id()
    solutions = package_util.get_solutions(task_id, None)
    for solution in solutions:
        cache_file: CacheFile = cache.get_cache_file(solution)
        assert cache_file.tests == {}


@pytest.mark.parametrize("create_package", [get_library_package_path()], indirect=True)
def test_extra_compilation_files_change(create_package, time_tool):
    """
    Test if after changing extra compilation files, all cached test results are removed.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()

    def change_file(file, comment_character):
        with open(file, "r") as f:
            source = f.read()
        with open(file, "w") as f:
            f.write(f"{comment_character} Changed source code.\n" + source)

    def test(file_to_change, lang, comment_character, extra_compilation_files=True):
        # First run to cache test results.
        command.run(args)

        # Change file
        change_file(os.path.join(os.getcwd(), "prog", file_to_change), comment_character)

        if extra_compilation_files:
            cache.process_extra_compilation_files(command.config.get("extra_compilation_files", []), command.ID)
        else:
            cache.process_extra_execution_files(command.config.get("extra_execution_files", {}), command.ID)
        task_id = package_util.get_task_id()
        solutions = package_util.get_solutions(task_id, None)
        for solution in solutions:
            if package_util.get_file_lang(solution) == lang:
                print(file_to_change, solution)
                assert not os.path.exists(paths.get_cache_path("md5sums", solution))
                info = cache.get_cache_file(solution)
                assert info == CacheFile()

    test("liblib.cpp", "cpp", "//")
    test("liblib.h", "cpp", "//")
    test("liblib.py", "py", "#", False)


@pytest.mark.parametrize("create_package", [get_simple_package_path()], indirect=True)
def test_contest_type_change(create_package, time_tool):
    """
    Test if after changing contest type, all cached test results are removed.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()

    # First run to cache test results.
    command.run(args)

    # Change contest type.
    config_path = os.path.join(os.getcwd(), "config.yml")
    with open(config_path, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    config["sinol_contest_type"] = "oi"
    with open(config_path, "w") as f:
        f.write(yaml.dump(config))

    # Compile checker check if test results are removed.
    command = Command()
    # We remove tests, so that `run()` exits before creating new cached test results.
    for test in glob.glob("in/*.in"):
        os.unlink(test)
    with pytest.raises(SystemExit):
        command.run(args)

    task_id = package_util.get_task_id()
    solutions = package_util.get_solutions(task_id, None)
    for solution in solutions:
        cache_file: CacheFile = cache.get_cache_file(solution)
        assert cache_file.tests == {}


@pytest.mark.parametrize("create_package", [get_simple_package_path()], indirect=True)
def test_cwd_in_prog(create_package, time_tool):
    """
    Test if `st-make` works when cwd is in prog.
    """
    package_path = create_package
    os.chdir("prog")
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run", "--time-tool", time_tool])
    command = Command()
    command.run(args)


@pytest.mark.parametrize("create_package", [get_checker_package_path()], indirect=True)
def test_ghost_checker(create_package):
    """
    Test if after removing a checker, the cached test results are removed.
    """
    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run"])
    command = Command()

    # First run to cache test results.
    command.run(args)

    # Remove checker.
    os.unlink(os.path.join(os.getcwd(), "prog", "chkchk.cpp"))
    shutil.copytree(paths.get_cache_path(), os.path.join(os.getcwd(), ".cache-copy"))

    command = Command()
    command.check_had_checker(False)

    for solution in os.listdir(paths.get_cache_path("md5sums")):
        cache_file: CacheFile = cache.get_cache_file(solution)
        assert cache_file.tests == {}

    shutil.rmtree(paths.get_cache_path())
    shutil.move(os.path.join(os.getcwd(), ".cache-copy"), paths.get_cache_path())

    # Run should fail, because outputs won't be checked with checker, so expected scores will be incorrect.
    command = Command()
    with pytest.raises(SystemExit) as e:
        command.run(args)
    assert e.value.code == 1


@pytest.mark.parametrize("create_package", [get_simple_package_path()], indirect=True)
def test_ignore_expected_flag(create_package, capsys):
    """
    Test flag --ignore-expected.
    """
    config = package_util.get_config()
    del config["sinol_expected_scores"]
    util.save_config(config)

    package_path = create_package
    create_ins_outs(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["run"])
    command = Command()

    with pytest.raises(SystemExit):
        command.run(args)
    out = capsys.readouterr().out
    assert "Use flag --apply-suggestions to apply suggestions." in out

    args = parser.parse_args(["run", "--ignore-expected"])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert "Ignoring expected scores." in out
