import glob

from sinol_make.commands.ingen.ingen_util import get_ingen, compile_ingen, run_ingen
from sinol_make.commands.outgen.outgen_util import get_correct_solution, compile_correct_solution, generate_output
from sinol_make.structs.gen_structs import OutputGenerationArguments
from sinol_make.helpers import package_util, compiler
from tests import util
from tests.fixtures import *


def test_get_ingen():
    """
    Test getting ingen.
    """
    simple_package_path = util.get_simple_package_path()
    gen_package_path = util.get_shell_ingen_pack_path()
    with tempfile.TemporaryDirectory() as tmpdir:
        shutil.copytree(simple_package_path, os.path.join(tmpdir, 'simple'))
        os.chdir(os.path.join(tmpdir, 'simple'))

        ingen_path = get_ingen("abc")
        assert os.path.basename(ingen_path) == "abcingen.cpp"

        ingen_path = get_ingen("abc", "prog/abcingen.cpp")
        assert os.path.basename(ingen_path) == "abcingen.cpp"

        with pytest.raises(SystemExit) as e:
            get_ingen("abc", "prog/abcingen.c")
        assert e.type == SystemExit
        assert e.value.code == 1

        shutil.copytree(gen_package_path, os.path.join(tmpdir, 'gen'))
        os.chdir(os.path.join(tmpdir, 'gen'))

        ingen_path = get_ingen("gen")
        assert os.path.basename(ingen_path) == "geningen.sh"

        with pytest.raises(SystemExit) as e:
            get_ingen("gen", "prog/geningen.cpp")
        assert e.type == SystemExit
        assert e.value.code == 1

        os.rename("prog/gen_helper.cpp", "prog/geningen.cpp")
        ingen_path = get_ingen("gen")
        assert os.path.basename(ingen_path) == "geningen.sh"


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_compile_ingen(create_package):
    """
    Test compilation of ingen.
    """
    task_id = package_util.get_task_id()
    ingen_path = get_ingen(task_id)
    args = compiler.get_default_compilers()
    executable = compile_ingen(ingen_path, args)
    assert os.path.exists(executable)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_get_correct_solution(create_package):
    """
    Test getting correct solution.
    """
    task_id = package_util.get_task_id()
    correct_solution_path = get_correct_solution(task_id)
    assert os.path.basename(correct_solution_path) == "abc.cpp"


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_compile_correct_solution(create_package):
    """
    Test compilation of correct solution.
    """
    task_id = package_util.get_task_id()
    correct_solution_path = get_correct_solution(task_id)
    args = compiler.get_default_compilers()
    executable = compile_correct_solution(correct_solution_path, args)
    assert os.path.exists(executable)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_run_ingen(create_package):
    """
    Test running ingen.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    ingen_path = get_ingen(task_id)
    args = compiler.get_default_compilers()
    executable = compile_ingen(ingen_path, args)

    run_ingen(executable)
    files = glob.glob(os.path.join(package_path, "in", "*.in"))
    files = [os.path.basename(file) for file in files]
    assert set(files) == {"abc1a.in", "abc2a.in", "abc3a.in", "abc4a.in"}


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_generate_output(create_package):
    """
    Test generating outputs.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    ingen_path = get_ingen(task_id)
    args = compiler.get_default_compilers()
    ingen_exe = compile_ingen(ingen_path, args)

    correct_solution = get_correct_solution(task_id)
    correct_sol_exe = compile_correct_solution(correct_solution, args)

    run_ingen(ingen_exe)
    assert generate_output(OutputGenerationArguments(correct_sol_exe, "in/abc1a.in", "out/abc1a.out"))
    assert os.path.exists(os.path.join(package_path, "out", "abc1a.out"))


@pytest.mark.parametrize("create_package", [util.get_bad_tests_package_path()], indirect=True)
def test_validate_tests(create_package, capsys):
    """
    Test validating test contents.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    ingen_path = get_ingen(task_id)
    args = compiler.get_default_compilers()
    ingen_exe = compile_ingen(ingen_path, args)
    run_ingen(ingen_exe)

    with open("in/bad6.in", "w") as f:
        f.write("1\n\n2 \n")
    with open("in/bad7.in", "w") as f:
        f.write("1 1\r\n")

    # (Test, error message)
    tests = [
        ("bad0.in", "Trailing whitespace in bad0.in:1"),
        ("bad1.in", "Leading whitespace in bad1.in:1"),
        ("bad2.in", "Tokens not separated by one space in bad2.in:1"),
        ("bad3.in", "Exactly one empty line expected in bad3.in"),
        ("bad4.in", "Trailing whitespace in bad4.in:2"),
        ("bad5.in", "No newline at the end of bad5.in"),
        ("bad6.in", "Trailing whitespace in bad6.in:3"),
        ("bad7.in", "Carriage return at the end of bad7.in:1"),
    ]

    for test, error in tests:
        valid, msg = package_util.validate_test(os.path.join(package_path, "in", test))
        assert not valid
        assert error in msg
