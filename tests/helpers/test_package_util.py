from sinol_make import Executor, TimeToolManager
from sinol_make.compilers.CompilersManager import CompilerManager
from sinol_make.programs.solution import Solution
from sinol_make.tests.input import InputTest
from ..fixtures import *
from tests import util
from sinol_make.helpers import package_util


@pytest.mark.parametrize("create_package", [util.get_long_name_package_path()], indirect=True)
def test_get_task_id(create_package):
    package_path = create_package
    assert package_util.get_task_id() == "lpn"
    with open(os.path.join(package_path, "config.yml"), "w") as config_file:
        config_file.write("title: Long package name\n")
    with pytest.raises(SystemExit):
        package_util.get_task_id()


def test_extract_test_id():
    assert package_util.extract_test_id("in/abc1a.in", "abc") == "1a"
    assert package_util.extract_test_id("in/abc10a.in", "abc") == "10a"
    assert package_util.extract_test_id("in/abc12ca.in", "abc") == "12ca"
    assert package_util.extract_test_id("in/abc0ocen.in", "abc") == "0ocen"
    assert package_util.extract_test_id("in/long_task_id2bc.in", "long_task_id") == "2bc"


def test_get_group():
    assert package_util.get_group("in/abc1a.in", "abc") == 1
    assert package_util.get_group("in/long_name2ocen.in", "long_name") == 0


def test_get_time_limit():
    os.chdir(util.get_simple_package_path())
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

    assert package_util.get_time_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "cpp", "abc") == 1000
    assert package_util.get_time_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "cpp", "abc") == 2000
    assert package_util.get_time_limit(InputTest("abc", "in/abc2b.in", exists=False), config, "cpp", "abc") == 2000
    assert package_util.get_time_limit(InputTest("abc", "in/abc3a.in", exists=False), config, "cpp", "abc") == 1000
    assert package_util.get_time_limit(InputTest("abc", "in/abc3ocen.in", exists=False), config, "cpp", "abc") == 5000

    assert package_util.get_time_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "py", "abc") == 2000
    assert package_util.get_time_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "py", "abc") == 3000
    assert package_util.get_time_limit(InputTest("abc", "in/abc2b.in", exists=False), config, "py", "abc") == 3000
    assert package_util.get_time_limit(InputTest("abc", "in/abc3a.in", exists=False), config, "py", "abc") == 2000
    assert package_util.get_time_limit(InputTest("abc", "in/abc3ocen.in", exists=False), config, "py", "abc") == 6000

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
    assert package_util.get_time_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "cpp", "abc") == 1000
    assert package_util.get_time_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "py", "abc") == 2000
    with pytest.raises(SystemExit):
        package_util.get_time_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "cpp", "abc")
    with pytest.raises(SystemExit):
        package_util.get_time_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "py", "abc")

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
    assert package_util.get_time_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "cpp", "abc") == 1000
    with pytest.raises(SystemExit):
        package_util.get_time_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "cpp", "abc")
    assert package_util.get_time_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "py", "abc") == 1000
    assert package_util.get_time_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "py", "abc") == 500


def test_get_memory_limit():
    os.chdir(util.get_simple_package_path())
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

    assert package_util.get_memory_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "cpp", "abc") == 256
    assert package_util.get_memory_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "cpp", "abc") == 512
    assert package_util.get_memory_limit(InputTest("abc", "in/abc2b.in", exists=False), config, "cpp", "abc") == 512
    assert package_util.get_memory_limit(InputTest("abc", "in/abc3ocen.in", exists=False), config, "cpp", "abc") == 128

    assert package_util.get_memory_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "py", "abc") == 512
    assert package_util.get_memory_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "py", "abc") == 1024
    assert package_util.get_memory_limit(InputTest("abc", "in/abc2b.in", exists=False), config, "py", "abc") == 1024
    assert package_util.get_memory_limit(InputTest("abc", "in/abc3ocen.in", exists=False), config, "py", "abc") == 256

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
    assert package_util.get_memory_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "cpp", "abc") == 1024
    assert package_util.get_memory_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "py", "abc") == 2048
    with pytest.raises(SystemExit):
        package_util.get_memory_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "cpp", "abc")
    with pytest.raises(SystemExit):
        package_util.get_memory_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "py", "abc")

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
    assert package_util.get_memory_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "cpp", "abc") == 1024
    with pytest.raises(SystemExit):
        package_util.get_memory_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "cpp", "abc")
    assert package_util.get_memory_limit(InputTest("abc", "in/abc1a.in", exists=False), config, "py", "abc") == 1024
    assert package_util.get_memory_limit(InputTest("abc", "in/abc2a.in", exists=False), config, "py", "abc") == 512


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_validate_files(create_package, capsys):
    package_path = create_package
    util.create_ins_outs(package_path)
    task_id = package_util.get_task_id()
    assert task_id == "abc"
    package_util.validate_test_names(task_id)

    os.rename(os.path.join(package_path, "in", "abc1a.in"), os.path.join(package_path, "in", "def1a.in"))
    with pytest.raises(SystemExit):
        package_util.validate_test_names(task_id)
    out = capsys.readouterr().out
    assert "def1a.in" in out

    os.rename(os.path.join(package_path, "in", "def1a.in"), os.path.join(package_path, "in", "abc1a.in"))
    os.rename(os.path.join(package_path, "out", "abc1a.out"), os.path.join(package_path, "out", "def1a.out"))
    with pytest.raises(SystemExit):
        package_util.validate_test_names(task_id)
    out = capsys.readouterr().out
    assert "def1a.out" in out


def test_get_executable_key():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        for task_id in ["abc", "long_task_id", "", "x"]:
            tt_manager = TimeToolManager()
            executor = Executor(tt_manager)
            compiler_manager = CompilerManager(None)

            def get_solution(path):
                os.makedirs("prog", exist_ok=True)
                with open(os.path.join("prog", path), "w") as f:
                    f.write("")
                return Solution(executor, compiler_manager, task_id, path)
            assert package_util.get_executable_key(get_solution(f"{task_id}1.cpp")) == (0, 1)
            assert package_util.get_executable_key(get_solution(f"{task_id}2.cpp")) == (0, 2)
            assert package_util.get_executable_key(get_solution(f"{task_id}s20.cpp")) == (1, 20)
            assert package_util.get_executable_key(get_solution(f"{task_id}s21.cpp")) == (1, 21)
            assert package_util.get_executable_key(get_solution(f"{task_id}b100.cpp")) == (2, 100)
            assert package_util.get_executable_key(get_solution(f"{task_id}b101.cpp")) == (2, 101)
            assert package_util.get_executable_key(get_solution(f"{task_id}1000_long.cpp")) == (0, 1000)
