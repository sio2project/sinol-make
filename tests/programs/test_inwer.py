from sinol_make.programs.inwer import Inwer
from tests.programs import util


def test():
    def test_func(program):
        assert program._use_fsanitize()
    util.tester([
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.cpp"],
            "class": Inwer,
            "progs": [None, "abcinwer.cpp", "prog/abcinwer.cpp"],
            "result": "abcinwer.cpp",
            "name": "inwer",
            "lang": "cpp",
            "dir": "prog",
            "test_func": test_func,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.py", "abcinwer.py"],
            "class": Inwer,
            "progs": [None, "abcinwer.py", "prog/abcinwer.py"],
            "result": "abcinwer.py",
            "name": "inwer",
            "lang": "py",
            "dir": "prog",
            "test_func": test_func,
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.py", "abcinwer2.cpp"],
            "class": Inwer,
            "progs": [None, "abcinwer2.cpp", "prog/abcinwer2.cpp"],
            "result": "abcinwer2.cpp",
            "name": "inwer",
            "lang": "cpp",
            "dir": "prog",
            "test_func": test_func,
        }
    ])
