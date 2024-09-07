import os
import pytest
import tempfile

from sinol_make.helpers.cache import save_compiled, check_compiled, create_cache_dirs
from tests import util
from tests.fixtures import create_package
from tests.commands.gen.test_integration import simple_run


def test_compilation_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        create_cache_dirs()
        with open(os.path.join(os.getcwd(), "test.txt"), "w") as f:
            f.write("Test data")
        with open(os.path.join(os.getcwd(), "test.e"), "w") as f:
            f.write("")

        assert check_compiled(os.path.join(os.getcwd(), "test.txt"), "default", False) is None
        save_compiled(os.path.join(os.getcwd(), "test.txt"),
                      os.path.join(os.getcwd(), "test.e"), "default", False)
        assert check_compiled(os.path.join(os.getcwd(), "test.txt"), "default", False) == \
               os.path.join(os.getcwd(), "test.e")


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path()], indirect=True)
def test_large_failed_output(create_package):
    """
    Test `ingen` command with large failed output.
    """
    with open(os.path.join(create_package, "prog", "geningen2.cpp"), "r") as f:
        code = f.read()
    code = code.replace("<<", "<")
    with open(os.path.join(create_package, "prog", "geningen2.cpp"), "w") as f:
        f.write(code)

    with pytest.raises(SystemExit):
        simple_run(["prog/geningen2.cpp"])
