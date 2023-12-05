import os
import subprocess

import pytest

from sinol_make import util
from sinol_make.timetools.sio2jail_cpu import Sio2jailCpuTimeTool
from sinol_make.timetools.sio2jail_real import Sio2jailRealTimeTool


def test_install():
    timetool = Sio2jailRealTimeTool()
    if timetool.is_latest_version():
        os.unlink(os.path.expanduser("~/.local/bin/sio2jail"))
    assert not timetool.is_latest_version()
    timetool.install()
    assert timetool.is_latest_version()


def test_is_available():
    timetools = [Sio2jailRealTimeTool()]
    if util.is_linux():
        timetools.append(Sio2jailCpuTimeTool())

    for timetool in timetools:
        if not timetool.is_latest_version():
            timetool.install()

        assert timetool.is_latest_version()
        assert timetool.is_available()

        if util.is_linux() and timetool.get_name() == "sio2jail":
            subprocess.run(["sudo", "sysctl", "kernel.perf_event_paranoid=0"])
            with pytest.raises(SystemExit):
                timetool.is_available()
