from typing import List

import pytest


def pytest_addoption(parser):
    parser.addoption("--github-runner", action="store_true", help="if set, will run tests specified for GitHub runner")


def pytest_collection_modifyitems(config, items: List[pytest.Item]):
    if config.getoption("--github-runner"):
        for item in items:
            if "github_runner" not in item.keywords:
                item.add_marker(pytest.mark.skip(reason="not for GitHub runner"))
    else:
        for item in items:
            if "github_runner" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="only for GitHub runner"))
