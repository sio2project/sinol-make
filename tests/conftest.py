from random import choices
from typing import List
import sys

import pytest


def pytest_addoption(parser):
    parser.addoption("--github-runner", action="store_true", help="if set, will run tests specified for GitHub runner")
    parser.addoption(
        '--time-tool',
        choices=['oiejq', 'time'],
        action='append',
        default=[],
        help='Time tool to use. Default: oiejq'
    )

def pytest_generate_tests(metafunc):
    if "time_tool" in metafunc.fixturenames:
        time_tools = []
        if metafunc.config.getoption("time_tool") != []:
            time_tools = metafunc.config.getoption("time_tool")
        elif sys.platform == "linux":
            time_tools = ["oiejq", "time"]
        else:
            time_tools = ["time"]
        metafunc.parametrize("time_tool", time_tools)

def pytest_collection_modifyitems(config, items: List[pytest.Item]):
    if config.getoption("--github-runner"):
        for item in items:
            if "github_runner" not in item.keywords:
                item.add_marker(pytest.mark.skip(reason="not for GitHub runner"))
    else:
        for item in items:
            if "github_runner" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="only for GitHub runner"))
