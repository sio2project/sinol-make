import os
import stat
import shutil
import subprocess
import tempfile

import pytest

from sinol_make.helpers import compile, package_util, paths
from sinol_make.helpers.cache import create_cache_dirs
from sinol_make.structs.compiler_structs import Compilers
from tests import util


def _mock_available():
    """Duckling tests need a working C++ compiler for the mock `duckc`."""
    return shutil.which("g++") is not None or shutil.which("c++") is not None


def test_duck_solutions_re():
    """`.dmf` files should be recognised as solutions."""
    solutions_re = package_util.get_solutions_re("duck")
    assert solutions_re.match("duck.dmf") is not None
    assert solutions_re.match("duck1.dmf") is not None
    assert solutions_re.match("ducks2.dmf") is not None
    assert solutions_re.match("duckb.dmf") is not None
    assert solutions_re.match("duck.txt") is None


def test_duck_in_code_files():
    """`get_all_code_files` should collect `.dmf` files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        os.makedirs("prog")
        for name in ["duck.dmf", "duck1.dmf", "duckingen.cpp"]:
            with open(os.path.join("prog", name), "w") as f:
                f.write("")
        code_files = [os.path.basename(f) for f in package_util.get_all_code_files("duck")]
        assert "duck.dmf" in code_files
        assert "duck1.dmf" in code_files


@pytest.mark.skipif(not _mock_available(), reason="No C++ compiler for the mock duckc")
def test_duck_compilation():
    """
    A `.dmf` solution should compile via `duckc` (the mock) and the resulting
    executable should run correctly.
    """
    duck_source = os.path.join(util.get_duck_package_path(), "prog", "duck.dmf")
    mock_duckc = util.get_mock_duck_compiler_path()

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        create_cache_dirs()

        program = os.path.join(tmpdir, "duck.dmf")
        shutil.copyfile(duck_source, program)
        output = paths.get_executables_path("duck.dmf.e")

        compilers = Compilers(duck_compiler_path=mock_duckc)
        assert compile.compile(program, output, compilers)
        assert os.path.exists(output)

        st = os.stat(output)
        os.chmod(output, st.st_mode | stat.S_IEXEC)
        result = subprocess.run([output], input="2 5\n", capture_output=True, text=True)
        assert result.stdout.strip() == "7"


@pytest.mark.skipif(not _mock_available(), reason="No C++ compiler for the mock duckc")
def test_duck_compile_file():
    """`compile_file` should work end to end for a `.dmf` solution."""
    duck_source = os.path.join(util.get_duck_package_path(), "prog", "duck.dmf")
    mock_duckc = util.get_mock_duck_compiler_path()

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        create_cache_dirs()
        # `compile_file` reads config.yml from the working directory.
        with open("config.yml", "w") as f:
            f.write("title: Duckling test\n")

        program = os.path.join(tmpdir, "duck.dmf")
        shutil.copyfile(duck_source, program)

        compilers = Compilers(duck_compiler_path=mock_duckc)
        exe, _ = compile.compile_file(program, "duck.dmf", compilers)
        assert exe is not None
        assert os.path.exists(exe)
