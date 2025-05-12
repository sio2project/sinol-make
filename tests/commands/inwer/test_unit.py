import argparse
import re

from ...fixtures import *
from ... import util
from sinol_make.helpers import package_util, compiler
from sinol_make.commands.inwer import inwer_util, InwerExecution
from sinol_make.commands.inwer import Command

from sio3pack.files import LocalFile
from sio3pack.test import Test

def test_get_inwer_path():
    """
    Test getting default and custom inwer.
    """
    os.chdir(util.get_inwer_package_path())
    task_id = package_util.get_task_id()
    assert inwer_util.get_inwer_path() is not None
    assert inwer_util.get_inwer_path('prog/werinwer2.cpp') == os.path.join(os.getcwd(), 'prog', 'werinwer2.cpp')


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_compile_inwer(create_package):
    """
    Test compilation of inwer.
    """
    task_id = package_util.get_task_id()
    inwer_path = inwer_util.get_inwer_path()
    args = compiler.get_default_compilers()
    executable = inwer_util.compile_inwer(inwer_path, args)
    assert os.path.exists(executable)


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_asserting_inwer(create_package):
    """
    Test asserting inwer.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    util.create_ins(package_path, task_id)
    inwer_path = os.path.join(os.getcwd(), 'prog', 'werinwer3.cpp')
    args = argparse.Namespace(
        c_compiler_path=compiler.get_c_compiler_path(),
        cpp_compiler_path=compiler.get_cpp_compiler_path(),
        python_interpreter_path=compiler.get_python_interpreter_path(),
        java_compiler_path=compiler.get_java_compiler_path()
    )
    executable = inwer_util.compile_inwer(inwer_path, args)

    execution = InwerExecution(
        inwer_exe_path=executable,
        test=Test('wer2a', '2a', LocalFile(os.path.join(os.getcwd(), 'in', 'wer2a.in')), None, '2'),
    )

    res = Command.verify_test(execution)
    assert res.valid is False
    assertion_re = re.compile(r'.*Assertion.*failed')
    print(res.output)
    print(assertion_re.match(res.output))
    assert assertion_re.match(res.output) is not None


def test_tests_comparator():
    for ti in ["abc", "long_task_id", ""]:
        assert [test.test_name for test in inwer_util.sort_tests(util.from_test_names(ti, [f"{ti}2a", f"{ti}1a"]))] == [f"{ti}1a", f"{ti}2a"]
        assert [test.test_name for test in inwer_util.sort_tests(util.from_test_names(ti, [f"{ti}2a", f"{ti}1a", f"{ti}1b"]))] == \
               [f"{ti}1a", f"{ti}1b", f"{ti}2a"]
        assert [test.test_name for test in inwer_util.sort_tests(util.from_test_names(ti, [f"{ti}2a", f"{ti}1a", f"{ti}1b", f"{ti}10a"]))] == \
                [f"{ti}1a", f"{ti}1b", f"{ti}2a", f"{ti}10a"]
        assert [test.test_name for test in inwer_util.sort_tests(util.from_test_names(ti, [f"{ti}2a", f"{ti}1a", f"{ti}1b", f"{ti}10a", f"{ti}10b"]))] == \
                [f"{ti}1a", f"{ti}1b", f"{ti}2a", f"{ti}10a", f"{ti}10b"]


def test_verify_tests_order():
    command = Command()
    command.task_id = "abc"
    command.tests = util.from_test_names("abc", ["abc1ocen", "abc2ocen", "abc3ocen",
                     "abc1a", "abc1b", "abc1c", "abc1d",
                     "abc2z", "abc2aa", "abc2ab", "abc2ac"])
    command.verify_tests_order()

    command.tests = util.from_test_names("abc", ["abc1ocen", "abc3ocen",
                     "abc1a", "abc1b", "abc1c", "abc1d",
                     "abc2z", "abc2aa", "abc2ab", "abc2ac"])
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests = util.from_test_names("abc", ["abc1ocen", "abc2ocen", "abc3ocen",
                     "abc1a", "abc1b", "abc1d",
                     "abc2z", "abc2aa", "abc2ab", "abc2ac"])
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests = util.from_test_names("abc", ["abc1ocen", "abc2ocen", "abc3ocen",
                     "abc1a", "abc1b", "abc1c", "abc1d",
                     "abc2z", "abc2ab", "abc2ac"])
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests = util.from_test_names("abc", ["abc9ocen", "abc10ocen", "abc11ocen",
                     "abc1a", "abc1b", "abc1c", "abc1d",
                     "abc2z", "abc2aa", "abc2ab", "abc2ac"])
    command.verify_tests_order()

    command.tests = util.from_test_names("abc", ["abc0", "abc0a", "abc0b",
                     "abc1", "abc1a", "abc1b"])
    command.verify_tests_order()

    command.tests = util.from_test_names("abc", ["abc0", "abc0b",
                     "abc1", "abc1a", "abc1b"])
    with pytest.raises(SystemExit):
        command.verify_tests_order()
