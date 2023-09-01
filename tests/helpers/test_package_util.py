from ..commands.run.util import create_ins
from ..fixtures import *
from sinol_make.helpers import package_util


def test_get_task_id(create_package):
    package_path = create_package
    assert package_util.get_task_id() == "abc"
    os.chdir(os.path.join(package_path, ".."))
    shutil.copytree(package_path, "Long name")
    os.chdir("Long name")
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
    assert package_util.get_executable("abc.cpp") == "abc.cpp.e"


def test_get_time_limit():
    config = {
        "time_limit": 1000,
        "time_limits": {
            "0": 5000,
            "2": 2000,
        },
        "override_limits": {
            "py": {
                "time_limit": 2000,
                "time_limits": {
                    "0": 6000,
                    "2": 3000,
                },
            }
        }
    }

    assert package_util.get_time_limit("in/abc1a.in", config, "cpp") == 1000
    assert package_util.get_time_limit("in/abc2a.in", config, "cpp") == 2000
    assert package_util.get_time_limit("in/abc2b.in", config, "cpp") == 2000
    assert package_util.get_time_limit("in/abc3a.in", config, "cpp") == 1000
    assert package_util.get_time_limit("in/abc3ocen.in", config, "cpp") == 5000

    assert package_util.get_time_limit("in/abc1a.in", config, "py") == 2000
    assert package_util.get_time_limit("in/abc2a.in", config, "py") == 3000
    assert package_util.get_time_limit("in/abc2b.in", config, "py") == 3000
    assert package_util.get_time_limit("in/abc3a.in", config, "py") == 2000
    assert package_util.get_time_limit("in/abc3ocen.in", config, "py") == 6000

    # Test getting default time limit.
    config = {
        "time_limits": {
            "1": 1000,
        },
        "override_limits": {
            "py": {
                "time_limits": {
                    "1": 2000,
                }
            }
        }
    }
    assert package_util.get_time_limit("in/abc1a.in", config, "cpp") == 1000
    assert package_util.get_time_limit("in/abc1a.in", config, "py") == 2000
    with pytest.raises(SystemExit):
        package_util.get_time_limit("in/abc2a.in", config, "cpp")
    with pytest.raises(SystemExit):
        package_util.get_time_limit("in/abc2a.in", config, "py")

    config = {
        "time_limits": {
            "1": 1000,
        },
        "override_limits": {
            "py": {
                "time_limit": 500,
                "time_limits": {
                    "1": 1000,
                }
            }
        }
    }
    assert package_util.get_time_limit("in/abc1a.in", config, "cpp") == 1000
    with pytest.raises(SystemExit):
        package_util.get_time_limit("in/abc2a.in", config, "cpp")
    assert package_util.get_time_limit("in/abc1a.in", config, "py") == 1000
    assert package_util.get_time_limit("in/abc2a.in", config, "py") == 500



def test_get_memory_limit():
    config = {
        "memory_limit": 256,
        "memory_limits": {
            "0": 128,
            "2": 512,
        },
        "override_limits": {
            "py": {
                "memory_limit": 512,
                "memory_limits": {
                    "0": 256,
                    "2": 1024,
                },
            }
        }
    }

    assert package_util.get_memory_limit("in/abc1a.in", config, "cpp") == 256
    assert package_util.get_memory_limit("in/abc2a.in", config, "cpp") == 512
    assert package_util.get_memory_limit("in/abc2b.in", config, "cpp") == 512
    assert package_util.get_memory_limit("in/abc3ocen.in", config, "cpp") == 128

    assert package_util.get_memory_limit("in/abc1a.in", config, "py") == 512
    assert package_util.get_memory_limit("in/abc2a.in", config, "py") == 1024
    assert package_util.get_memory_limit("in/abc2b.in", config, "py") == 1024
    assert package_util.get_memory_limit("in/abc3ocen.in", config, "py") == 256

    # Test getting default memory limit.
    config = {
        "memory_limits": {
            "1": 1024,
        },
        "override_limits": {
            "py": {
                "memory_limits": {
                    "1": 2048,
                }
            }
        }
    }
    assert package_util.get_memory_limit("in/abc1a.in", config, "cpp") == 1024
    assert package_util.get_memory_limit("in/abc1a.in", config, "py") == 2048
    with pytest.raises(SystemExit):
        package_util.get_memory_limit("in/abc2a.in", config, "cpp")
    with pytest.raises(SystemExit):
        package_util.get_memory_limit("in/abc2a.in", config, "py")

    config = {
        "memory_limits": {
            "1": 1024,
        },
        "override_limits": {
            "py": {
                "memory_limit": 512,
                "memory_limits": {
                    "1": 1024,
                }
            }
        }
    }
    assert package_util.get_memory_limit("in/abc1a.in", config, "cpp") == 1024
    with pytest.raises(SystemExit):
        package_util.get_memory_limit("in/abc2a.in", config, "cpp")
    assert package_util.get_memory_limit("in/abc1a.in", config, "py") == 1024
    assert package_util.get_memory_limit("in/abc2a.in", config, "py") == 512
