import argparse
import re

from ...fixtures import *
from ... import util
from sinol_make.helpers import package_util, compiler
from sinol_make.commands.inwer import inwer_util, InwerExecution
from sinol_make.commands.inwer import Command


def test_get_inwer_path():
    """
    Test getting default and custom inwer.
    """
    os.chdir(util.get_inwer_package_path())
    task_id = package_util.get_task_id()
    assert inwer_util.get_inwer_path(task_id) is not None
    assert inwer_util.get_inwer_path(task_id, 'prog/werinwer2.cpp') == os.path.join(os.getcwd(), 'prog', 'werinwer2.cpp')


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_compile_inwer(create_package):
    """
    Test compilation of inwer.
    """
    task_id = package_util.get_task_id()
    inwer_path = inwer_util.get_inwer_path(task_id)
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
        test_name='wer2a.in',
        test_path=os.path.join(os.getcwd(), 'in', 'wer2a.in'),
    )

    res = Command.verify_test(execution)
    assert res.valid is False
    assertion_re = re.compile(r'.*Assertion.*failed')
    print(res.output)
    print(assertion_re.match(res.output))
    assert assertion_re.match(res.output) is not None


def test_tests_comparator():
    for ti in ["abc", "long_task_id", ""]:
        assert inwer_util.sort_tests([f"{ti}2a.in", f"{ti}1a.in"], ti) == [f"{ti}1a.in", f"{ti}2a.in"]
        assert inwer_util.sort_tests([f"{ti}2a.in", f"{ti}1a.in", f"{ti}1b.in"], ti) == \
               [f"{ti}1a.in", f"{ti}1b.in", f"{ti}2a.in"]
        assert inwer_util.sort_tests([f"{ti}2a.in", f"{ti}1a.in", f"{ti}1b.in", f"{ti}10a.in"], ti) == \
                [f"{ti}1a.in", f"{ti}1b.in", f"{ti}2a.in", f"{ti}10a.in"]
        assert inwer_util.sort_tests([f"{ti}2a.in", f"{ti}1a.in", f"{ti}1b.in", f"{ti}10a.in", f"{ti}10b.in"], ti) == \
                [f"{ti}1a.in", f"{ti}1b.in", f"{ti}2a.in", f"{ti}10a.in", f"{ti}10b.in"]


def test_verify_tests_order():
    command = Command()
    command.task_id = "abc"
    command.tests = ["abc1ocen.in", "abc2ocen.in", "abc3ocen.in",
                     "abc1a.in", "abc1b.in", "abc1c.in", "abc1d.in",
                     "abc2z.in", "abc2aa.in", "abc2ab.in", "abc2ac.in"]
    command.verify_tests_order()

    command.tests.remove("abc2ocen.in")
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests.append("abc2ocen.in")
    command.tests.remove("abc1c.in")
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests.append("abc1c.in")
    command.tests.remove("abc2aa.in")
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests.append("abc2aa.in")
    command.tests.remove("abc1ocen.in")
    command.tests.remove("abc2ocen.in")
    command.tests.remove("abc3ocen.in")
    command.tests.append("abc9ocen.in")
    command.tests.append("abc10ocen.in")
    command.tests.append("abc11ocen.in")

    command.verify_tests_order()

    command.tests = ["abc0.in", "abc0a.in", "abc0b.in",
                     "abc1.in", "abc1a.in", "abc1b.in"]
    command.verify_tests_order()

    command.tests.remove("abc0a.in")
    with pytest.raises(SystemExit):
        command.verify_tests_order()
