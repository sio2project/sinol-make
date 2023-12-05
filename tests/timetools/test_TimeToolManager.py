import argparse

from sinol_make import TimeToolManager, util


def test_get_possible_timetools():
    timetool_manager = TimeToolManager()
    assert len(timetool_manager.get_possible_timetools()) == 2


def get_available_timetools():
    timetool_manager = TimeToolManager()
    if util.is_wsl() or util.is_macos():
        assert len(timetool_manager.get_available_timetools()) == 1
        assert timetool_manager.get_available_timetools()[0].get_name() == "time"
    else:
        assert len(timetool_manager.get_available_timetools()) == 2
        assert set([timetool.get_name() for timetool in timetool_manager.get_available_timetools()]) == \
               {"time", "sio2jail"}


def test_get_default_timetool():
    timetool_manager = TimeToolManager()
    if util.is_wsl() or util.is_macos():
        assert timetool_manager.get_default_timetool().get_name() == "time"
    else:
        assert timetool_manager.get_default_timetool().get_name() == "sio2jail"


def test_set_timetool():
    timetool_manager = TimeToolManager()
    if util.is_linux():
        timetool_manager.set_timetool(argparse.Namespace(time_tool="sio2jail"))
        assert timetool_manager.used_timetool.get_name() == "sio2jail"

    timetool_manager.set_timetool(argparse.Namespace(time_tool="time"))
    assert timetool_manager.used_timetool.get_name() == "time"
