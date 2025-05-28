import pytest

from ..commands.run.util import create_ins
from ..fixtures import *
from tests import util
from sinol_make.helpers import package_util, func_cache


def test_get_tests(create_package):
    SIO3Package.reset()
    os.chdir(create_package)
    task_id = package_util.get_task_id()
    create_ins(create_package, task_id)
    tests = package_util.get_tests()
    assert list(map(lambda t: t.test_name, tests)) == ["abc1a", "abc2a", "abc3a", "abc4a"]

    with tempfile.TemporaryDirectory() as tmpdir:
        def create_file(name):
            with open(os.path.join(tmpdir, "in", name), "w") as f:
                f.write("")

        SIO3Package.reset()
        os.chdir(tmpdir)
        with open(os.path.join(tmpdir, "config.yml"), "w") as f:
            f.write("sinol_task_id: abc")
        os.mkdir("in")
        create_file("abc0.in")
        create_file("abc0a.in")
        create_file("abc1ocen.in")
        create_file("abc2ocen.in")
        create_file("abc1a.in")
        create_file("abc1b.in")
        create_file("abc2a.in")
        os.mkdir("out")
        package_util.reload_tests()

        assert set(map(lambda t: t.test_name, package_util.get_tests())) == \
               {"abc0", "abc0a", "abc1a", "abc1b", "abc1ocen", "abc2a", "abc2ocen"}
        assert list(map(lambda t: t.test_name, package_util.get_tests(["in/abc1a.in"]))) == ["abc1a"]
        assert list(map(lambda t: t.test_name, package_util.get_tests(["in/abc??.in"]))) == \
               ["abc0a", "abc1a", "abc1b", "abc2a"]
        assert list(map(lambda t: t.test_name, package_util.get_tests(["abc1a.in"]))) == ["abc1a"]
        assert list(map(lambda t: t.test_name, package_util.get_tests(["abc?ocen.in", "abc0.in"]))) == ["abc0", "abc1ocen", "abc2ocen"]
        assert list(map(lambda t: t.test_name, package_util.get_tests([os.path.join(tmpdir, "in", "abc1a.in")]))) == ["abc1a"]


def test_get_executable():
    assert package_util.get_executable("abc.cpp") == "abc.cpp.e"


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_validate_files(create_package, capsys):
    package_path = create_package
    util.create_ins_outs(package_path)
    task_id = package_util.get_task_id()
    assert task_id == "abc"
    package_util.validate_test_names()

    os.rename(os.path.join(package_path, "in", "abc1a.in"), os.path.join(package_path, "in", "def1a.in"))
    package_util.reload_tests()
    with pytest.raises(SystemExit):
        package_util.validate_test_names()
    out = capsys.readouterr().out
    assert "def1a.in" in out

    os.rename(os.path.join(package_path, "in", "def1a.in"), os.path.join(package_path, "in", "abc1a.in"))
    os.rename(os.path.join(package_path, "out", "abc1a.out"), os.path.join(package_path, "out", "def1a.out"))
    package_util.reload_tests()
    with pytest.raises(SystemExit):
        package_util.validate_test_names()
    out = capsys.readouterr().out
    assert "def1a.out" in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_get_executable_key(create_package):
    for task_id in ["abc", "long_task_id", "x"]:
        with open(os.path.join(create_package, "config.yml"), "w") as f:
            f.write(f"sinol_task_id: {task_id}")
        SIO3Package().reload_config()
        assert package_util.get_executable_key(f"{task_id}1.cpp.e") == (0, 1)
        assert package_util.get_executable_key(f"{task_id}2.cpp.e") == (0, 2)
        assert package_util.get_executable_key(f"{task_id}s20.cpp.e") == (1, 20)
        assert package_util.get_executable_key(f"{task_id}s21.cpp.e") == (1, 21)
        assert package_util.get_executable_key(f"{task_id}b100.cpp.e") == (2, 100)
        assert package_util.get_executable_key(f"{task_id}b101.cpp.e") == (2, 101)
        assert package_util.get_executable_key(f"{task_id}x1000.cpp.e") == (0, 0)


def test_get_solutions():
    SIO3Package.reset()
    os.chdir(get_simple_package_path())

    def to_filenames(solutions):
        return [sol.filename for sol in solutions]

    solutions = to_filenames(package_util.get_solutions())
    assert solutions == ["abc.cpp", "abc1.cpp", "abc2.cpp", "abc3.cpp", "abc4.cpp"]
    solutions = to_filenames(package_util.get_solutions(["prog/abc.cpp"]))
    assert solutions == ["abc.cpp"]
    assert "abc1.cpp" not in solutions

    with tempfile.TemporaryDirectory() as tmpdir:
        def create_file(name):
            with open(os.path.join(tmpdir, "prog", name), "w") as f:
                f.write("")

        SIO3Package.reset()
        os.chdir(tmpdir)
        os.mkdir("in")
        os.mkdir("out")
        os.mkdir("prog")
        with open(os.path.join(tmpdir, "config.yml"), "w") as f:
            f.write("sinol_task_id: abc")

        create_file("abc.cpp")
        create_file("abc1.cpp")
        create_file("abc2.cpp")
        create_file("abcs1.cpp")
        create_file("abcs2.cpp")

        assert to_filenames(package_util.get_solutions()) == ["abc.cpp", "abc1.cpp", "abc2.cpp", "abcs1.cpp", "abcs2.cpp"]
        assert to_filenames(package_util.get_solutions(["prog/abc.cpp"])) == ["abc.cpp"]
        assert to_filenames(package_util.get_solutions(["abc.cpp"])) == ["abc.cpp"]
        assert to_filenames(package_util.get_solutions([os.path.join(tmpdir, "prog", "abc.cpp")])) == ["abc.cpp"]
        assert to_filenames(package_util.get_solutions(["prog/abc?.cpp"])) == ["abc1.cpp", "abc2.cpp"]
        assert to_filenames(package_util.get_solutions(["abc?.cpp"])) == ["abc1.cpp", "abc2.cpp"]
        assert to_filenames(package_util.get_solutions(["prog/abc*.cpp"])) == ["abc.cpp", "abc1.cpp", "abc2.cpp", "abcs1.cpp", "abcs2.cpp"]
        assert to_filenames(package_util.get_solutions(["abc*.cpp"])) == ["abc.cpp", "abc1.cpp", "abc2.cpp", "abcs1.cpp", "abcs2.cpp"]
        assert to_filenames(package_util.get_solutions(["prog/abc.cpp", "abc1.cpp"])) == ["abc.cpp", "abc1.cpp"]
        assert to_filenames(package_util.get_solutions(["prog/abc.cpp", "abc?.cpp"])) == ["abc.cpp", "abc1.cpp", "abc2.cpp"]
        assert to_filenames(package_util.get_solutions(["abc.cpp", "abc2.cpp", "abcs2.cpp"])) == ["abc.cpp", "abc2.cpp", "abcs2.cpp"]
