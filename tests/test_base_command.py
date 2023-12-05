import os
import tempfile

from sinol_make import TimeToolManager, Executor
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.programs.checker import Checker
from sinol_make.programs.ingen import Ingen
from sinol_make.programs.inwer import Inwer
from sinol_make.programs.solution import Solution
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest

from tests.util import create_prog_files, create_in_files, create_out_files, clear_cwd


def get_command():
    timetool_manager = TimeToolManager()
    executor = Executor(timetool_manager)
    command = BaseCommand(timetool_manager, executor)
    return command


def get_tester(cls, func, tests, pass_argument = True):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        for test in tests:
            create_prog_files(*test["files"])
            if pass_argument:
                prog = func(test.get("prog", None))
            else:
                prog = func()
            if isinstance(prog, list):
                for p in prog:
                    assert isinstance(p, cls), test
            else:
                assert isinstance(prog, cls), test

            if isinstance(test["result"], list):
                for res in test["result"]:
                    assert res in [p.basename for p in prog], test
            else:
                assert prog.file_path == os.path.join(tmpdir, "prog", f"{test['result']}"), test
            clear_cwd()


def test_get_ingen():
    command = get_command()
    command.task_id = "abc"
    get_tester(Ingen, command.get_ingen, [
        {"files": ["abcingen.cpp", "abcingen2.cpp"], "result": "abcingen.cpp"},
        {"files": ["abcingen.sh", "abcingen.cpp", "abcingen2.cpp"], "result": "abcingen.sh"},
        {
            "files": ["abcingen.sh", "abcingen.cpp", "abcingen2.cpp"],
            "prog": "abcingen2.cpp",
            "result": "abcingen2.cpp"
        },
        {
            "files": ["abcingen.sh", "abcingen.cpp", "abcingen2.cpp"],
            "prog": "prog/abcingen2.cpp",
            "result": "abcingen2.cpp"
        },
        {"files": ["abcingen2.cpp"], "result": "abcingen2.cpp"},
    ])


def test_get_inwer():
    command = get_command()
    command.task_id = "abc"
    get_tester(Inwer, command.get_inwer, [
        {"files": ["abcinwer.cpp", "abcinwer2.cpp"], "result": "abcinwer.cpp"},
        {
            "files": ["abcinwer.cpp", "abcinwer2.cpp"],
            "prog": "abcinwer2.cpp",
            "result": "abcinwer2.cpp"
        },
        {
            "files": ["abcinwer.cpp", "abcinwer2.cpp"],
            "prog": "prog/abcinwer2.cpp",
            "result": "abcinwer2.cpp"
        },
        {"files": ["abcinwer2.cpp"], "result": "abcinwer2.cpp"},
    ])


def test_get_checker():
    command = get_command()
    command.task_id = "abc"
    get_tester(Checker, command.get_checker, [
        {"files": ["abcchk.cpp", "abcchk2.cpp"], "result": "abcchk.cpp"},
    ])


def test_get_solution():
    command = get_command()
    command.task_id = "abc"
    get_tester(Solution, command.get_solution, [
        {"files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"], "result": "abc.cpp"},
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"],
            "prog": "abc2.cpp",
            "result": "abc2.cpp"
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"],
            "prog": "prog/abcs3.py",
            "result": "abcs3.py"
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"],
            "prog": "prog/abcb10.cpp",
            "result": "abcb10.cpp"
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"],
            "prog": "prog/abc4_long.py",
            "result": "abc4_long.py"
        },
    ])


def test_get_all_solutions():
    command = get_command()
    command.task_id = "abc"
    get_tester(Solution, command.get_all_solutions, [
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "result": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"]
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "prog": ["abc2.cpp"],
            "result": ["abc2.cpp"]
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "prog": ["prog/abcs3.py", "abc2.cpp", "prog/abc4_long.py"],
            "result": ["abcs3.py", "abc2.cpp", "abc4_long.py"]
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "prog": ["prog/abcs3.py", "abc2.cpp", "prog/abc4_long.py", "prog/abcb10.cpp"],
            "result": ["abcs3.py", "abc2.cpp", "abc4_long.py", "abcb10.cpp"]
        }
    ])


def test_get_correct_solution():
    command = get_command()
    command.task_id = "abc"
    get_tester(Solution, command.get_correct_solution, [
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"],
            "result": "abc.cpp"
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "result": "abc.cpp"
        },
    ], pass_argument=False)


def exists_tester(func, tests):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        for test in tests:
            create_prog_files(*test["files"])
            assert func() == test["result"], test
            clear_cwd()


def test_ingen_exists():
    command = get_command()
    command.task_id = "abc"
    exists_tester(command.ingen_exists, [
        {
            "files": ["abcingen.cpp", "abcingen2.cpp"],
            "result": True,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "result": True,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"],
            "result": False,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "result": True,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcchk.cpp", "abcinwer.py"],
            "result": True,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcchk.cpp", "abcinwer.py"],
            "result": False,
        },
    ])


def test_checker_exists():
    command = get_command()
    command.task_id = "abc"
    exists_tester(command.checker_exists, [
        {
            "files": ["abcchk.cpp", "abcchk2.cpp"],
            "result": True,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "result": True,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py"],
            "result": False,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.sh", "abcingen.cpp", "abcinwer.py"],
            "result": False,
        },
    ])


def test_get_corresponding_test():
    command = get_command()
    command.task_id = "abc"
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        for type, cls1, cls2, files in [("in", InputTest, OutputTest, ["abc1.in", "abc2.in", "abc3.in"]),
                                        ("out", OutputTest, InputTest, ["abc1.out", "abc2.out", "abc3.out"])]:
            if type == "in":
                create_in_files(*files)
            else:
                create_out_files(*files)

            for file in files:
                for exists in [False, True]:
                    if exists:
                        if type == "in":
                            create_out_files(os.path.splitext(file)[0] + ".out")
                        else:
                            create_in_files(os.path.splitext(file)[0] + ".in")
                    input = cls1("abc", file)
                    output = command.get_corresponding_test(input, exists=exists)
                    print(input, output)
                    assert isinstance(output, cls2), (type, exists, file)
                    if type == "in":
                        assert output.basename == os.path.splitext(input.basename)[0] + ".out", (type, exists, file)
                    else:
                        assert output.basename == os.path.splitext(input.basename)[0] + ".in", (type, exists, file)
                    assert output.exists() == exists
            clear_cwd()
