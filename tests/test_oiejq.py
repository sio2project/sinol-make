import os
import shutil
import sys
from urllib.request import urlretrieve
import pytest

from sinol_make import oiejq, util


@pytest.mark.github_runner
def test_install_oiejq():
    if sys.platform != 'linux':
        return

    try:
        os.remove(os.path.expanduser('~/.local/bin/oiejq'))
        os.remove(os.path.expanduser('~/.local/bin/sio2jail'))
    except IsADirectoryError:
        shutil.rmtree(os.path.expanduser('~/.local/bin/oiejq'), ignore_errors=True)
    except FileNotFoundError:
        pass
    assert not oiejq.check_oiejq()
    assert oiejq.install_oiejq()
    assert oiejq.get_oiejq_path() == os.path.expanduser('~/.local/bin/oiejq')

    try:
        os.remove(os.path.expanduser('~/.local/bin/oiejq'))
        os.remove(os.path.expanduser('~/.local/bin/sio2jail'))
    except FileNotFoundError:
        pass

    assert not oiejq.check_oiejq()
    os.makedirs(os.path.expanduser('~/.local/bin/oiejq'))
    with pytest.raises(SystemExit):
        oiejq.install_oiejq()

    # Test if oiejq is reinstalled when oiejq.sh is changed
    os.rmdir(os.path.expanduser('~/.local/bin/oiejq'))
    oiejq.install_oiejq()
    with open(os.path.expanduser('~/.local/bin/oiejq'), 'a') as f:
        f.write('\n')
    assert not oiejq.check_oiejq()
    oiejq.install_oiejq()


@pytest.mark.github_runner
def test_check_oiejq():
    if sys.platform != 'linux':
        return

    try:
        os.remove(os.path.expanduser('~/.local/bin/oiejq'))
        os.remove(os.path.expanduser('~/.local/bin/sio2jail'))
    except IsADirectoryError:
        shutil.rmtree(os.path.expanduser('~/.local/bin/oiejq'), ignore_errors=True)
    except FileNotFoundError:
        pass

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
    assert oiejq._check_if_oiejq_executable(os.path.expanduser('~/.local/bin/oiejq'))


@pytest.mark.github_runner
def test_perf_counters_not_set():
    """
    Test `oiejq.check_perf_counters_enabled` with perf counters disabled
    """
    if sys.platform != 'linux':
        return

    oiejq.install_oiejq()
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


@pytest.mark.github_runner
def test_updating():
    """
    Test updating oiejq
    """
    if sys.platform != 'linux':
        return
    try:
        os.remove(os.path.expanduser('~/.local/bin/oiejq'))
        os.remove(os.path.expanduser('~/.local/bin/sio2jail'))
    except IsADirectoryError:
        shutil.rmtree(os.path.expanduser('~/.local/bin/oiejq'), ignore_errors=True)
    except FileNotFoundError:
        pass
    assert not oiejq.check_oiejq()
    assert oiejq.install_oiejq()
    assert oiejq.get_oiejq_path() == os.path.expanduser('~/.local/bin/oiejq')

    # Download older sio2jail
    urlretrieve('https://github.com/sio2project/sio2jail/releases/download/v1.4.3/sio2jail',
                os.path.expanduser('~/.local/bin/sio2jail'))
    os.chmod(os.path.expanduser('~/.local/bin/sio2jail'), 0o777)
    assert not oiejq.check_oiejq()
    assert oiejq.install_oiejq()
    assert oiejq.check_oiejq()
