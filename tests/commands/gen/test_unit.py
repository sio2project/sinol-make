import os
import tempfile
import pytest
import shutil
import glob

from sinol_make.commands.gen import gen_util, OutputGenerationArguments
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

        ingen_path = gen_util.get_ingen()
        assert os.path.basename(ingen_path) == "abcingen.cpp"

        ingen_path = gen_util.get_ingen("abc")
        assert os.path.basename(ingen_path) == "abcingen.cpp"

        ingen_path = gen_util.get_ingen("abc", "prog/abcingen.cpp")
        assert os.path.basename(ingen_path) == "abcingen.cpp"

        with pytest.raises(SystemExit) as e:
            gen_util.get_ingen("abc", "prog/abcingen.c")
        assert e.type == SystemExit
        assert e.value.code == 1

        shutil.copytree(gen_package_path, os.path.join(tmpdir, 'gen'))
        os.chdir(os.path.join(tmpdir, 'gen'))

        ingen_path = gen_util.get_ingen()
        assert os.path.basename(ingen_path) == "geningen.sh"

        ingen_path = gen_util.get_ingen("gen")
        assert os.path.basename(ingen_path) == "geningen.sh"

        with pytest.raises(SystemExit) as e:
            gen_util.get_ingen("gen", "prog/geningen.cpp")
        assert e.type == SystemExit
        assert e.value.code == 1

        os.rename("prog/gen_helper.cpp", "prog/geningen.cpp")
        ingen_path = gen_util.get_ingen("gen")
        assert os.path.basename(ingen_path) == "geningen.sh"


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_compile_ingen(create_package):
    """
    Test compilation of ingen.
    """
    task_id = package_util.get_task_id()
    ingen_path = gen_util.get_ingen(task_id)
    args = compiler.get_default_compilers()
    executable = gen_util.compile_ingen(ingen_path, args)
    assert os.path.exists(executable)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_get_correct_solution(create_package):
    """
    Test getting correct solution.
    """
    task_id = package_util.get_task_id()
    correct_solution_path = gen_util.get_correct_solution(task_id)
    assert os.path.basename(correct_solution_path) == "abc.cpp"


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_compile_correct_solution(create_package):
    """
    Test compilation of correct solution.
    """
    task_id = package_util.get_task_id()
    correct_solution_path = gen_util.get_correct_solution(task_id)
    args = compiler.get_default_compilers()
    executable = gen_util.compile_correct_solution(correct_solution_path, args)
    assert os.path.exists(executable)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_run_ingen(create_package):
    """
    Test running ingen.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    ingen_path = gen_util.get_ingen(task_id)
    args = compiler.get_default_compilers()
    executable = gen_util.compile_ingen(ingen_path, args)

    gen_util.run_ingen(executable)
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
    ingen_path = gen_util.get_ingen(task_id)
    args = compiler.get_default_compilers()
    ingen_exe = gen_util.compile_ingen(ingen_path, args)

    correct_solution = gen_util.get_correct_solution(task_id)
    correct_sol_exe = gen_util.compile_correct_solution(correct_solution, args)

    gen_util.run_ingen(ingen_exe)
    assert gen_util.generate_output(OutputGenerationArguments(correct_sol_exe, "in/abc1a.in", "out/abc1a.out"))
    assert os.path.exists(os.path.join(package_path, "out", "abc1a.out"))
