from ..commands.run.util import create_ins
from ..fixtures import *
from sinol_make.helpers import package_util


def test_get_task_id(create_package):
    assert package_util.get_task_id() == "abc"


def test_extract_test_id():
    assert package_util.extract_test_id("in/abc1a.in") == "1a"
    assert package_util.extract_test_id("in/abc10a.in") == "10a"
    assert package_util.extract_test_id("in/abc12ca.in") == "12ca"
    assert package_util.extract_test_id("in/abc0ocen.in") == "0ocen"


def test_get_group():
    assert package_util.get_group("in/abc1a.in") == 1


def test_get_tests(create_package):
    create_ins(create_package)
    os.chdir(create_package)
    tests = package_util.get_tests(None)
    assert tests == ["in/abc1a.in", "in/abc2a.in", "in/abc3a.in", "in/abc4a.in"]


def test_extract_file_name():
    assert package_util.get_file_name("in/abc1a.in") == "abc1a.in"


def test_get_executable():
    assert package_util.get_executable("abc.cpp") == "abc.e"


def test_get_time_limit():
    config = {
        "time_limit": 1000,
        "time_limits": {
            "0": 5000,
            "2": 2000,
        }
    }

    assert package_util.get_time_limit("in/abc1a.in", config) == 1000
    assert package_util.get_time_limit("in/abc2b.in", config) == 2000
    assert package_util.get_time_limit("in/abc3ocen.in", config) == 5000


def test_get_memory_limit():
    config = {
        "memory_limit": 256,
        "memory_limits": {
            "0": 128,
            "2": 512,
        }
    }

    assert package_util.get_memory_limit("in/abc1a.in", config) == 256
    assert package_util.get_memory_limit("in/abc2a.in", config) == 512
    assert package_util.get_memory_limit("in/abc2b.in", config) == 512
    assert package_util.get_memory_limit("in/abc3ocen.in", config) == 128
