import os
import sys
import tempfile

from sinol_make.helpers import compile, compiler


def test_compilation_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        with open(os.path.join(os.getcwd(), "test.txt"), "w") as f:
            f.write("Test data")
        with open(os.path.join(os.getcwd(), "test.e"), "w") as f:
            f.write("")

        assert compile.check_compiled(os.path.join(os.getcwd(), "test.txt")) is None
        compile.save_compiled(os.path.join(os.getcwd(), "test.txt"),
                              os.path.join(os.getcwd(), "test.e"))
        assert compile.check_compiled(os.path.join(os.getcwd(), "test.txt")) == os.path.join(os.getcwd(), "test.e")


def test_get_cpp_standard():
    if sys.platform == "darwin":
        assert compiler.get_cpp_standard("g++-12") == "c++20"
    else:
        assert compiler.get_cpp_standard("g++") == "c++20"
