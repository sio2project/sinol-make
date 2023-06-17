import os
import sys
import pytest

from sinol_make import util


@pytest.mark.github_runner
def test_install_oiejq():
    if sys.platform != 'linux':
        return

    if util.check_oiejq():
        os.remove(sys.path.expanduser('~/.local/bin/oiejq'))
        assert not util.check_oiejq()

    assert util.install_oiejq()
