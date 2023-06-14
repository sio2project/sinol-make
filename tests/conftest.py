from typing import List

import pytest


def pytest_addoption(parser):
    parser.addoption("--oij-access", action="store_true", help="if set, will run tests that require access to oij.edu.pl")


def pytest_collection_modifyitems(config, items: List[pytest.Item]):
    for item in items:
        if "oij_access" in item.keywords and not config.getoption("--oij-access"):
            item.add_marker(pytest.mark.skip(reason="need --oij-access option to run"))