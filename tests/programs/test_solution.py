from sinol_make.programs.solution import Solution
from tests.programs import util


def test():
    def test_func(program):
        assert program._use_extras()

    def test_bad(program):
        test_func(program)
        assert program.is_bad()

    def test_slow(program):
        test_func(program)
        assert program.is_slow()

    def test_normal(program):
        test_func(program)
        assert program.is_normal()

    util.tester([
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "class": Solution,
            "progs": ["abc.cpp", "prog/abc.cpp"],
            "result": "abc.cpp",
            "name": "solution",
            "lang": "cpp",
            "dir": "prog",
            "test_func": test_normal,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.py", "abcinwer.py"],
            "class": Solution,
            "progs": ["abc2.cpp", "prog/abc2.cpp"],
            "result": "abc2.cpp",
            "name": "solution",
            "lang": "cpp",
            "dir": "prog",
            "test_func": test_normal,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.py", "abcinwer2.cpp"],
            "class": Solution,
            "progs": ["abcs3.py", "prog/abcs3.py"],
            "result": "abcs3.py",
            "name": "solution",
            "lang": "py",
            "dir": "prog",
            "test_func": test_slow,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.py", "abcinwer2.cpp"],
            "class": Solution,
            "progs": ["abcb10.cpp", "prog/abcb10.cpp"],
            "result": "abcb10.cpp",
            "name": "solution",
            "lang": "cpp",
            "dir": "prog",
            "test_func": test_bad,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abcs4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.py", "abcinwer2.cpp"],
            "class": Solution,
            "progs": ["abcs4_long.py", "prog/abcs4_long.py"],
            "result": "abcs4_long.py",
            "name": "solution",
            "lang": "py",
            "dir": "prog",
            "test_func": test_slow,
        },
    ])
