import os
import sys
import pytest

from sinol_make import oiejq


@pytest.mark.github_runner
def test_install_oiejq():
    if sys.platform != 'linux':
        return

    if oiejq.check_oiejq():
        os.remove(os.path.expanduser('~/.local/bin/oiejq'))
        assert not oiejq.check_oiejq()

    assert oiejq.install_oiejq()


@pytest.mark.github_runner
def test_perf_counters_not_set():
    """
    Test `oiejq.check_perf_counters_enabled` with perf counters disabled
    """
    if sys.platform != 'linux':
        return

    with pytest.raises(SystemExit):
        oiejq.check_perf_counters_enabled()


@pytest.mark.oiejq
def test_perf_counters_set():
    """
    Test `oiejq.check_perf_counters_enabled` with perf counters enabled
    """
    oiejq.check_perf_counters_enabled()
