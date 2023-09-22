import os
import tempfile

from sinol_make.helpers.cache import save_compiled, check_compiled


def test_compilation_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        with open(os.path.join(os.getcwd(), "test.txt"), "w") as f:
            f.write("Test data")
        with open(os.path.join(os.getcwd(), "test.e"), "w") as f:
            f.write("")

        assert check_compiled(os.path.join(os.getcwd(), "test.txt")) is None
        save_compiled(os.path.join(os.getcwd(), "test.txt"),
                                               os.path.join(os.getcwd(), "test.e"))
        assert check_compiled(os.path.join(os.getcwd(), "test.txt")) == os.path.join(os.getcwd(), "test.e")
