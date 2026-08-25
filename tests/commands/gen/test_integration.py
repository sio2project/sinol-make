import sys

import yaml
import glob

from sinol_make import configure_parsers
from sinol_make import util as sm_util
from sinol_make.commands.gen import Command
from sinol_make.commands.ingen import Command as IngenCommand
from sinol_make.commands.ingen.ingen_util import get_ingen
from sinol_make.commands.outgen import Command as OutgenCommand
from sinol_make.commands.run import Command as RunCommand
from sinol_make.helpers import package_util, paths, cache
from tests.fixtures import *
from tests import util


def simple_run(arguments=None, command="gen"):
    if arguments is None:
        arguments = []
    parser = configure_parsers()
    args = parser.parse_args([command] + arguments)
    if command == "gen":
        command = Command()
    elif command == "ingen":
        command = IngenCommand()
    elif command == "outgen":
        command = OutgenCommand()
    else:
        raise ValueError("Invalid command")
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
    task_id = package_util.get_task_id()
    correct_solution = package_util.get_correct_solution(task_id)
    cache.save_compiled(correct_solution, "exe", "default", False)
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
    task_id = package_util.get_task_id()
    correct_solution = package_util.get_correct_solution(task_id)
    cache.save_compiled(correct_solution, "exe", "default", False)
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


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path()], indirect=True)
def test_shell_ingen_unchanged(create_package):
    """
    Test if ingen.sh is unchanged after running `ingen` command.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    shell_ingen_path = get_ingen(task_id)
    assert os.path.splitext(shell_ingen_path)[1] == ".sh"
    edited_time = os.path.getmtime(shell_ingen_path)
    simple_run()
    assert edited_time == os.path.getmtime(shell_ingen_path)


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_only_inputs_flag(create_package):
    """
    Test if `--only-inputs` flag works.
    """
    simple_run(["--only-inputs"])
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    assert len(ins) > 0
    assert len(outs) == 0
    assert not os.path.exists(os.path.join(create_package, "in", ".md5sums"))


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_ingen(create_package):
    """
    Test if `ingen` command works.
    """
    simple_run(None, "ingen")
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    assert len(ins) > 0
    assert len(outs) == 0
    assert not os.path.exists(os.path.join(create_package, "in", ".md5sums"))


@pytest.mark.parametrize("create_package", [util.get_static_tests_package_path()], indirect=True)
def test_static_test_ingen_interaction(create_package):
    """
    Tests if a static test (stt1a.in) was ignored by `ingen`,
    but it sill generated a test down the line (stt1b.in).
    """
    stt1a = os.path.join(create_package, "in", "stt1a.in")
    edited_stt1a = os.path.getmtime(stt1a)

    stt1b = os.path.join(create_package, "in", "stt1b.in")
    assert not os.path.exists(stt1b)

    config = package_util.get_config()
    config["sinol_static_tests"] = "stt1a.in"
    with open(os.path.join(create_package, "config.yml"), "w") as f:
        yaml.dump(config, f)

    simple_run(None, "ingen")
    assert edited_stt1a == os.path.getmtime(stt1a)
    assert os.path.exists(stt1b)


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                            indirect=True)
def test_only_outputs_flag(create_package):
    """
    Test if `--only-outputs` flag works.
    """
    simple_run(['--only-inputs'])
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    in1 = ins[0]
    for file in ins[1:]:
        os.unlink(file)
    assert len(outs) == 0
    def in_to_out(file):
        return os.path.join(create_package, "out", os.path.basename(file).replace(".in", ".out"))

    simple_run(["--only-outputs"])
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    assert len(ins) == 1
    assert os.path.exists(in_to_out(in1))
    assert len(outs) == 1


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_outgen(create_package):
    """
    Test if `outgen` command works.
    """
    simple_run(None, "ingen")
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    in1 = ins[0]
    for file in ins[1:]:
        os.unlink(file)
    assert len(outs) == 0
    def in_to_out(file):
        return os.path.join(create_package, "out", os.path.basename(file).replace(".in", ".out"))

    simple_run(None, "outgen")
    ins = glob.glob(os.path.join(create_package, "in", "*.in"))
    outs = glob.glob(os.path.join(create_package, "out", "*.out"))
    assert len(ins) == 1
    assert os.path.exists(in_to_out(in1))
    assert len(outs) == 1


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_missing_output_files(create_package):
    """
    Test if `ingen` command generates missing output files.
    """
    package_path = create_package
    for args in [[], ["--only-outputs"]]:
        simple_run()
        outs = glob.glob(os.path.join(package_path, "out", "*.out"))
        os.unlink(outs[0])
        assert not os.path.exists(outs[0])
        simple_run(args)
        assert os.path.exists(outs[0])
        shutil.rmtree(paths.get_cache_path())
        os.unlink(os.path.join(package_path, "in", ".md5sums"))
        cache.create_cache_dirs()


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path(), util.get_simple_package_path()],
                         indirect=True)
def test_correct_solution_changed(create_package):
    """
    Test if `.md5sums` is deleted when correct solution is changed.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    md5sums = os.path.join(package_path, "in", ".md5sums")
    simple_run()
    assert os.path.exists(md5sums)
    outputs = {}
    for output in glob.glob(os.path.join(package_path, "out", "*.out")):
        outputs[os.path.basename(output)] = sm_util.get_file_md5(output)

    solution = package_util.get_correct_solution(task_id)
    with open(os.path.join(solution), "w") as f:
        f.write("int main() {}")
    cache.check_correct_solution(task_id)
    assert not os.path.exists(md5sums)
    simple_run()
    assert os.path.exists(md5sums)
    for output in glob.glob(os.path.join(package_path, "out", "*.out")):
        assert outputs[os.path.basename(output)] != sm_util.get_file_md5(output)


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path()], indirect=True)
def test_fsanitize(create_package):
    """
    Test if ingen is compiled with -fsanitize=address,undefined flags.
    """
    if sm_util.is_macos_arm():
        pytest.skip("-fsanitize=address,undefined is not supported on Apple Silicon")
    for ingen in ["prog/geningen3.cpp", "prog/geningen4.cpp"]:
        with pytest.raises(SystemExit) as e:
            simple_run(["--sanitize", "simple", ingen])
        assert e.type == SystemExit
        assert e.value.code == 1


@pytest.mark.parametrize("create_package", [util.get_bad_tests_package_path()], indirect=True)
def test_bad_tests(create_package, capsys):
    """
    Test if validation of test contents works.
    """

    # Gen should fail
    with pytest.raises(SystemExit) as e:
        simple_run()
    assert e.type == SystemExit
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Trailing whitespace in bad0.in:1" in out

    # Generate tests without validation
    simple_run(["--no-validate"], command="ingen")

    # (program, should fail, error message)
    tests = [
        ("bad.cpp", False, ""),
        ("bad1.cpp", True, "Trailing whitespace in bad0.out:1"),
        ("bad2.cpp", True, "Leading whitespace in bad0.out:1"),
        ("bad3.cpp", True, "Tokens not separated by one space in bad0.out:1"),
        ("bad4.cpp", True, "No newline at the end of bad0.out"),
        ("bad5.cpp", True, "Exactly one empty line expected in bad0.out"),
    ]

    for program, should_fail, error_message in tests:
        if program != "bad.cpp":
            shutil.copyfile(os.path.join(create_package, "prog", program), os.path.join(create_package, "prog", "bad.cpp"))
        if not should_fail:
            simple_run(command="outgen")
        else:
            with pytest.raises(SystemExit) as e:
                simple_run(command="outgen")
            assert e.type == SystemExit
            assert e.value.code == 1
            out = capsys.readouterr().out
            assert error_message in out

        for file in glob.glob(os.path.join(create_package, "out", "*.out")):
            os.unlink(file)
        os.unlink(os.path.join(create_package, "in", ".md5sums"))


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path()], indirect=True)
def test_dangling_inputs(create_package, capsys):
    """
    Test if dangling input files are removed.
    """
    simple_run(["prog/geningen5.cpp"], command="ingen")
    for f in ["gen1.in", "gen2.in"]:
        assert os.path.exists(os.path.join(create_package, "in", f))
    _ = capsys.readouterr().out

    simple_run(["prog/geningen6.cpp"], command="ingen")
    out = capsys.readouterr().out
    assert ("Old input files won't be deleted, because static tests are not defined. "
            "You can define them in config.yml with `sinol_static_tests` key.") in out

    config = package_util.get_config()
    config["sinol_static_tests"] = []
    sm_util.save_config(config)
    simple_run(["prog/geningen6.cpp"], command="ingen")
    out = capsys.readouterr().out
    assert "Cleaning up old input files." in out
    assert not os.path.exists(os.path.join(create_package, "in", "gen1.in"))
    assert os.path.exists(os.path.join(create_package, "in", "gen2.in"))

    config = package_util.get_config()
    config["sinol_static_tests"] = "gen1.in"
    sm_util.save_config(config)
    simple_run(["prog/geningen5.cpp"], command="ingen")
    for f in ["gen1.in", "gen2.in"]:
        assert os.path.exists(os.path.join(create_package, "in", f))
    _ = capsys.readouterr().out
    simple_run(["prog/geningen6.cpp"], command="ingen")
    out = capsys.readouterr().out
    for f in ["gen1.in", "gen2.in"]:
        assert os.path.exists(os.path.join(create_package, "in", f))

    # Test if globbing works correctly
    config = package_util.get_config()
    config["sinol_static_tests"] = ["gen?.in"]
    sm_util.save_config(config)
    simple_run(["prog/geningen5.cpp"], command="ingen")
    for f in ["gen1.in", "gen2.in"]:
        assert os.path.exists(os.path.join(create_package, "in", f))
    simple_run(["prog/geningen7.cpp"], command="ingen")
    for f in ["gen1.in", "gen2.in"]:
        assert os.path.exists(os.path.join(create_package, "in", f))


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_outgen_cache_cleaning(create_package, capsys):
    """
    Test if cache is cleaned after running outgen.
    """
    simple_run(command="gen")
    parser = configure_parsers()
    args = parser.parse_args(["run"])
    RunCommand().run(args)

    with open(os.path.join(create_package, "prog", "abcingen.cpp"), "r") as f:
        code = f.read().replace("1 3", "1 4")
    with open(os.path.join(create_package, "prog", "abcingen.cpp"), "w") as f:
        f.write(code)

    simple_run(command="ingen")

    # Run should fail, because input file was changed, but output file was not regenerated.
    with pytest.raises(SystemExit) as e:
        RunCommand().run(args)
    assert e.type == SystemExit
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Solution abc.cpp passed group 1 with status WA while it should pass with status OK." in out

    simple_run(command="outgen")
    # Run should pass, because output file was regenerated and cache for this test was cleaned.
    RunCommand().run(args)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_cache_remove_after_flags_change(create_package):
    """
    Test if cache for a program is removed if compilation flags change or -fsanitize is disabled.
    """
    def random_key_to_cache():
        cache_file = cache.get_cache_file("abcingen.cpp")
        print(cache_file)
        cache_dict = cache_file.to_dict()
        cache_dict["random_key"] = "random_value"
        with open(paths.get_cache_path("md5sums", "abcingen.cpp"), "w") as f:
            yaml.dump(cache_dict, f)

    def check_assert():
        with open(paths.get_cache_path("md5sums", "abcingen.cpp"), "r") as f:
            cache_dict = yaml.load(f, Loader=yaml.FullLoader)
        assert "random_key" not in cache_dict

    # Generate cache
    simple_run(command="gen")
    random_key_to_cache()
    simple_run(["--compile-mode", "oioioi"], command="gen")
    check_assert()

    if sm_util.is_macos_arm():  # -fsanitize=address,undefined is not supported on Apple Silicon
        return
    # Generate cache
    simple_run(command="gen")
    random_key_to_cache()
    simple_run(["--sanitize", "simple"], command="gen")
    check_assert()


@pytest.mark.parametrize("create_package", [util.get_simple_interactive_package()], indirect=True)
def test_no_outputs_interactive(create_package, capsys):
    """
    Test if ingen command works with interactive tasks.
    """
    simple_run(command="gen")
    assert os.path.exists(os.path.join(create_package, "in", "int1.in"))
    assert not os.path.exists(os.path.join(create_package, "out", "int1.out"))
    out = capsys.readouterr().out
    assert "Outgen is not supported for this task type." in out

    with pytest.raises(SystemExit) as e:
        simple_run(command="outgen")
    assert e.type == SystemExit
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Output generation is not supported for this task type." in out


def force_regeneration(package_path, input_basename):
    """
    Forces the regeneration of the output file for the given input test
    by invalidating the input's md5 sum in `in/.md5sums`.
    """
    md5_sums = get_md5_sums(package_path)
    md5_sums[input_basename] = "0"
    with open(os.path.join(package_path, "in", ".md5sums"), "w") as f:
        yaml.dump(md5_sums, f)


def write_output(package_path, output_basename, content):
    """
    Writes the given content to an output file, as if it was written by hand.
    """
    path = os.path.join(package_path, "out", output_basename)
    with open(path, "w") as f:
        f.write(content)
    return path


def read_file(path):
    with open(path, "r") as f:
        return f.read()


@pytest.mark.parametrize("create_package", [util.get_checker_package_path()], indirect=True)
def test_correct_handwritten_output(capsys, create_package):
    """
    Test if a hand-written output file which the checker accepts is left unchanged.
    """
    package_path = create_package
    simple_run()
    # A different, but correct answer for chk1a.
    output = write_output(package_path, "chk1a.out", "0\n")
    force_regeneration(package_path, "chk1a.in")
    capsys.readouterr()

    simple_run()
    out = capsys.readouterr().out
    assert "1 output files were not generated by sinol-make and won't be overwritten." in out
    assert "Verifying 1 output files which were not generated by sinol-make." in out
    assert "Output file chk1a.out is correct, leaving it unchanged." in out
    assert read_file(output) == "0\n"


@pytest.mark.parametrize("create_package", [util.get_checker_package_path()], indirect=True)
def test_wrong_handwritten_output(capsys, create_package):
    """
    Test if a hand-written output file which the checker rejects fails outgen
    without being overwritten.
    """
    package_path = create_package
    simple_run()
    # An answer which is greater than the sum of all numbers, which the checker rejects.
    output = write_output(package_path, "chk1a.out", "1000000\n")
    force_regeneration(package_path, "chk1a.in")
    capsys.readouterr()

    with pytest.raises(SystemExit) as e:
        simple_run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Output file chk1a.out is wrong." in out
    assert "run this command with the --overwrite flag" in out
    assert read_file(output) == "1000000\n"
    # The correct solution's output is kept for inspection.
    assert read_file(paths.get_outgen_path("chk1a.out")).strip() == "6"


@pytest.mark.parametrize("create_package", [util.get_checker_package_path()], indirect=True)
def test_overwrite_flag(create_package):
    """
    Test if `--overwrite` overwrites hand-written output files.
    """
    package_path = create_package
    simple_run()
    output = write_output(package_path, "chk1a.out", "1000000\n")
    force_regeneration(package_path, "chk1a.in")

    simple_run(["--overwrite"])
    assert read_file(output).strip() == "6"


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_edited_output_without_checker(capsys, create_package):
    """
    Test if an edited output file is verified against the correct solution's output
    when the package has no checker.
    """
    package_path = create_package
    simple_run()
    output = write_output(package_path, "abc1a.out", "42\n")
    force_regeneration(package_path, "abc1a.in")
    capsys.readouterr()

    with pytest.raises(SystemExit) as e:
        simple_run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Output file abc1a.out is wrong." in out
    assert read_file(output) == "42\n"


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_generated_outputs_overwritten(capsys, create_package):
    """
    Test if output files generated by sinol-make are overwritten without verification.
    """
    package_path = create_package
    simple_run()
    output = os.path.join(package_path, "out", "abc1a.out")
    contents = read_file(output)
    force_regeneration(package_path, "abc1a.in")
    capsys.readouterr()

    simple_run()
    out = capsys.readouterr().out
    assert "Verifying" not in out
    assert "Successfully generated output file abc1a.out" in out
    assert read_file(output) == contents


@pytest.mark.parametrize("create_package", [util.get_example_tests_package_path()], indirect=True)
def test_legacy_package_example_outputs(capsys, create_package):
    """
    Test if example outputs of a package generated by a version of sinol-make which didn't
    keep track of generated outputs are verified instead of being overwritten.
    """
    package_path = create_package
    simple_run()
    os.unlink(os.path.join(package_path, "out", ".md5sums"))
    output = write_output(package_path, "exa0.out", "42\n")
    force_regeneration(package_path, "exa0.in")
    capsys.readouterr()

    with pytest.raises(SystemExit) as e:
        simple_run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Output file exa0.out is wrong." in out
    assert read_file(output) == "42\n"


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_legacy_package_generated_outputs(capsys, create_package):
    """
    Test if outputs of a package generated by a version of sinol-make which didn't keep track
    of generated outputs are still overwritten when they are not example outputs.
    """
    package_path = create_package
    simple_run()
    os.unlink(os.path.join(package_path, "out", ".md5sums"))
    # Simulate an output generated by an older version of the correct solution.
    output = write_output(package_path, "abc1a.out", "42\n")
    force_regeneration(package_path, "abc1a.in")
    capsys.readouterr()

    simple_run()
    out = capsys.readouterr().out
    assert "Verifying" not in out
    assert read_file(output) != "42\n"
