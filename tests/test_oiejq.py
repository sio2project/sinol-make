import os
import shutil
import sys
import pytest

from sinol_make import oiejq, util


@pytest.mark.github_runner
def test_install_oiejq():
    if sys.platform != 'linux':
        return

    shutil.rmtree(os.path.expanduser('~/.local/bin/'), ignore_errors=True)
    assert not oiejq.check_oiejq()
    assert oiejq.install_oiejq()
    assert oiejq.get_oiejq_path() == os.path.expanduser('~/.local/bin/oiejq')

    shutil.rmtree(os.path.expanduser('~/.local/bin/'), ignore_errors=True)
    assert not oiejq.check_oiejq()
    os.makedirs(os.path.expanduser('~/.local/bin/oiejq'))
    with pytest.raises(SystemExit):
        oiejq.install_oiejq()


@pytest.mark.github_runner
def test_check_oiejq():
    if sys.platform != 'linux':
        return

    shutil.rmtree(os.path.expanduser('~/.local/bin/'), ignore_errors=True)
    assert not oiejq.check_oiejq()
    os.makedirs(os.path.expanduser('~/.local/bin/oiejq'), exist_ok=True)
    assert not oiejq.check_oiejq()
    os.rmdir(os.path.expanduser('~/.local/bin/oiejq'))
    with open(os.path.expanduser('~/.local/bin/oiejq'), 'w') as f:
        f.write('abcdef')
    assert not oiejq.check_oiejq()
    os.chmod(os.path.expanduser('~/.local/bin/oiejq'), 0o777)
    assert not oiejq.check_oiejq()
    with open(os.path.expanduser('~/.local/bin/oiejq'), 'w') as f:
        f.write('#!/bin/bash\necho "test"')
    assert oiejq.check_oiejq()


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
    if not util.is_linux():
        return
    oiejq.check_perf_counters_enabled()
