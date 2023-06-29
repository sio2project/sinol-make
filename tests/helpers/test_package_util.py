from ..commands.run.util import get_command, create_ins
from ..fixtures import *
from sinol_make.helpers import package_util


def test_get_task_id(create_package):
    assert package_util.get_task_id() == "abc"


def test_extract_test_no():
    assert package_util.extract_test_no("in/abc1a.in") == "1a"
    assert package_util.extract_test_no("in/abc10a.in") == "10a"
    assert package_util.extract_test_no("in/abc12ca.in") == "12ca"
    assert package_util.extract_test_no("in/abc0ocen.in") == "0ocen"


def test_get_group():
    assert package_util.get_group("in/abc1a.in") == 1


def test_get_tests(create_package):
    command = get_command(create_package)
    create_ins(create_package, command)
    os.chdir(create_package)
    tests = package_util.get_tests(None)
    assert tests == ["in/abc1a.in", "in/abc2a.in", "in/abc3a.in", "in/abc4a.in"]
