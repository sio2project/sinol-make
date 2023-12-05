from sinol_make.programs.checker import Checker
from tests.programs import util


def test():
    util.tester([
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.cpp", "abcinwer.py"],
            "class": Checker,
            "progs": [None, "abcchk.cpp", "prog/abcchk.cpp"],
            "result": "abcchk.cpp",
            "name": "checker",
            "lang": "cpp",
            "dir": "prog",
        },
        {
            "files": ["abc.cpp", "abc2.cpp", "abcs3.py", "abcb10.cpp", "abc4_long.py",
                      "abcingen.cpp", "abcingen.sh", "abcchk.py", "abcinwer.py"],
            "class": Checker,
            "progs": [None, "abcchk.py", "prog/abcchk.py"],
            "result": "abcchk.py",
            "name": "checker",
            "lang": "py",
            "dir": "prog",
        }
    ])
