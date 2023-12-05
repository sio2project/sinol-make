from sinol_make.programs.ingen import Ingen
from tests.programs import util


def test():
    def test_func(program):
        assert program._use_fsanitize()

    def test_shell(program):
        test_func(program)
        assert program.is_shell_ingen()
        assert program.basename == "abcingen.sh"
    util.tester([
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcchk.cpp", "abcinwer.py"],
            "class": Ingen,
            "progs": [None, "abcingen.cpp", "prog/abcingen.cpp"],
            "result": "abcingen.cpp",
            "name": "ingen",
            "lang": "cpp",
            "dir": "prog",
            "test_func": test_func,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.py", "abcchk.py", "abcinwer.py"],
            "class": Ingen,
            "progs": [None, "abcingen.py", "prog/abcingen.py"],
            "result": "abcingen.py",
            "name": "ingen",
            "lang": "py",
            "dir": "prog",
            "test_func": test_func,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "class": Ingen,
            "progs": ["abcingen.sh", "prog/abcingen.sh"],
            "result": "abcingen.sh",
            "name": "ingen",
            "lang": "sh",
            "dir": "prog",
            "test_func": test_func,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "class": Ingen,
            "result": "abcingen.sh",
            "name": "ingen",
            "lang": "sh",
            "dir": "prog",
            "test_func": test_shell,
        }
    ])
