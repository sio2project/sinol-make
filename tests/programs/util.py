import os
import tempfile

from sinol_make import TimeToolManager, Executor
from sinol_make.compilers.CompilersManager import CompilerManager
from sinol_make.programs.program import Program
from tests import util


def test_program(program: Program, cls, name: str, lang: str, dir: str):
    assert isinstance(program, cls)
    assert program.get_name() == name
    assert program.get_lang() == lang
    assert program.get_dir() == dir


def tester(tests):
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        timetool_manager = TimeToolManager()
        executor = Executor(timetool_manager)
        compiler_manager = CompilerManager(None)
        for test in tests:
            for file in test.get("files", []):
                util.create_prog_files(file)

            cls = test["class"]
            for prog in test.get("progs", [None]):
                program = cls(executor, compiler_manager, "abc", prog)
                assert isinstance(program, cls), (test, prog)
                assert program.basename == os.path.basename(test["result"]), (test, prog)
                test_program(program, cls, test["name"], test["lang"], test["dir"])
                if "test_func" in test:
                    test["test_func"](program)
            util.clear_cwd()
