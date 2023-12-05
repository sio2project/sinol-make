import re

from sinol_make.tests.input import InputTest
from tests.fixtures import *
from tests import util
from sinol_make.helpers import package_util
from sinol_make.commands.inwer import inwer_util, InwerExecution
from sinol_make.commands.inwer import Command


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_asserting_inwer(create_package):
    """
    Test asserting inwer.
    """
    package_path = create_package
    task_id = package_util.get_task_id()
    util.create_ins(package_path, task_id)
    command = util.get_inwer_command()
    command.base_run(None)
    inwer = command.get_inwer("prog/werinwer3.cpp")
    exe, _ = inwer.compile()
    assert exe is not None
    test = InputTest(task_id, "in/wer2a.in")
    execution = InwerExecution(
        inwer=inwer,
        test=test,
    )

    res = Command.verify_test(execution)
    assert res.valid is False
    assertion_re = re.compile(r'.*Assertion.*failed')
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
    def convert_arr_to_tests(tests):
        return [InputTest("abc", test, exists=False) for test in tests]

    os.chdir(util.get_simple_package_path())
    command = util.get_inwer_command()
    command.task_id = "abc"
    command.tests = convert_arr_to_tests(["abc1ocen.in", "abc2ocen.in", "abc3ocen.in",
                                          "abc1a.in", "abc1b.in", "abc1c.in", "abc1d.in",
                                          "abc2z.in", "abc2aa.in", "abc2ab.in", "abc2ac.in"])
    command.verify_tests_order()

    command.tests = convert_arr_to_tests(["abc1ocen.in", "abc3ocen.in",
                                          "abc1a.in", "abc1b.in", "abc1c.in", "abc1d.in",
                                          "abc2z.in", "abc2aa.in", "abc2ab.in", "abc2ac.in"])
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests = convert_arr_to_tests(["abc1ocen.in", "abc2ocen.in", "abc3ocen.in",
                                          "abc1a.in", "abc1b.in", "abc1d.in",
                                          "abc2z.in", "abc2aa.in", "abc2ab.in", "abc2ac.in"])
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests = convert_arr_to_tests(["abc1ocen.in", "abc2ocen.in", "abc3ocen.in",
                                          "abc1a.in", "abc1b.in", "abc1c.in", "abc1d.in",
                                          "abc2z.in", "abc2ab.in", "abc2ac.in"])
    with pytest.raises(SystemExit):
        command.verify_tests_order()

    command.tests = convert_arr_to_tests(["abc9ocen.in", "abc10ocen.in", "abc11ocen.in",
                                          "abc1a.in", "abc1b.in", "abc1c.in", "abc1d.in",
                                          "abc2z.in", "abc2aa.in", "abc2ab.in", "abc2ac.in"])
    command.verify_tests_order()
