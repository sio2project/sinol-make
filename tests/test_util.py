import os
import sys
import pytest
import tempfile

from sinol_make import util


@pytest.mark.github_runner
def test_install_oiejq():
    if sys.platform != 'linux':
        return

    if util.check_oiejq():
        os.remove(sys.path.expanduser('~/.local/bin/oiejq'))
        assert not util.check_oiejq()

    assert util.install_oiejq()


def test_file_diff():
    with tempfile.TemporaryDirectory() as tmpdir:
        a_file = os.path.join(tmpdir, 'a')
        b_file = os.path.join(tmpdir, 'b')

        open(a_file, 'w').write("1"
                                "2"
                                "3")

        open(b_file, 'w').write("1"
                                "2"
                                "3"
                                "4")

        assert util.file_diff(a_file, b_file) is False

        open(a_file, 'w').write("1\n")
        open(b_file, 'w').write("1        ")

        assert util.file_diff(a_file, b_file) is True

        open(a_file, 'w').write("1\n")
        open(b_file, 'w').write("1\n\n")

        assert util.file_diff(a_file, b_file) is False
