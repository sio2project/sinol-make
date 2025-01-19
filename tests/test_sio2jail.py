import os
import shutil
import sys
from urllib.request import urlretrieve
import pytest

from sinol_make import sio2jail, util


@pytest.mark.github_runner
def test_install_sio2jail():
    if not sio2jail.sio2jail_supported():
        return

    try:
        if os.path.exists(os.path.expanduser('~/.local/bin/oiejq')):
            os.remove(os.path.expanduser('~/.local/bin/oiejq'))
        if os.path.exists(os.path.expanduser('~/.local/bin/sio2jail')):
            os.remove(os.path.expanduser('~/.local/bin/sio2jail'))
    except IsADirectoryError:
        shutil.rmtree(os.path.expanduser('~/.local/bin/oiejq'), ignore_errors=True)
    assert not sio2jail.check_sio2jail()
    assert sio2jail.install_sio2jail()
    assert sio2jail.get_default_sio2jail_path() == os.path.expanduser('~/.local/bin/sio2jail')

    if os.path.exists(os.path.expanduser('~/.local/bin/oiejq')):
        os.remove(os.path.expanduser('~/.local/bin/oiejq'))
    if os.path.exists(os.path.expanduser('~/.local/bin/sio2jail')):
        os.remove(os.path.expanduser('~/.local/bin/sio2jail'))

    assert not sio2jail.check_sio2jail()
    sio2jail.install_sio2jail()


@pytest.mark.github_runner
def test_check_sio2jail():
    if not sio2jail.sio2jail_supported():
        return

    try:
        if os.path.exists(os.path.expanduser('~/.local/bin/oiejq')):
            os.remove(os.path.expanduser('~/.local/bin/oiejq'))
        if os.path.exists(os.path.expanduser('~/.local/bin/sio2jail')):
            os.remove(os.path.expanduser('~/.local/bin/sio2jail'))
    except IsADirectoryError:
        shutil.rmtree(os.path.expanduser('~/.local/bin/oiejq'), ignore_errors=True)

    assert not sio2jail.check_sio2jail()
    os.makedirs(os.path.expanduser('~/.local/bin/oiejq'), exist_ok=True)
    assert not sio2jail.check_sio2jail()
    os.rmdir(os.path.expanduser('~/.local/bin/oiejq'))
    with open(os.path.expanduser('~/.local/bin/oiejq'), 'w') as f:
        f.write('abcdef')
    assert not sio2jail.check_sio2jail()


@pytest.mark.github_runner
def test_perf_counters_not_set():
    """
    Test `sio2jail.check_perf_counters_enabled` with perf counters disabled
    """
    if not sio2jail.sio2jail_supported():
        return

    sio2jail.install_sio2jail()
    with pytest.raises(SystemExit):
        sio2jail.check_perf_counters_enabled()


@pytest.mark.sio2jail
def test_perf_counters_set():
    """
    Test `sio2jail.check_perf_counters_enabled` with perf counters enabled
    """
    if not sio2jail.sio2jail_supported():
        return
    sio2jail.check_perf_counters_enabled()


@pytest.mark.github_runner
def test_updating():
    """
    Test updating sio2jail
    """
    if not sio2jail.sio2jail_supported():
        return
    try:
        os.remove(os.path.expanduser('~/.local/bin/oiejq'))
        os.remove(os.path.expanduser('~/.local/bin/sio2jail'))
    except IsADirectoryError:
        shutil.rmtree(os.path.expanduser('~/.local/bin/oiejq'), ignore_errors=True)
    except FileNotFoundError:
        pass
    assert not sio2jail.check_sio2jail()
    assert sio2jail.install_sio2jail()
    assert sio2jail.get_default_sio2jail_path() == os.path.expanduser('~/.local/bin/sio2jail')

    # Download older sio2jail
    urlretrieve('https://github.com/sio2project/sio2jail/releases/download/v1.4.3/sio2jail',
                os.path.expanduser('~/.local/bin/sio2jail'))
    os.chmod(os.path.expanduser('~/.local/bin/sio2jail'), 0o777)
    assert not sio2jail.check_sio2jail()
    assert sio2jail.install_sio2jail()
    assert sio2jail.check_sio2jail()
