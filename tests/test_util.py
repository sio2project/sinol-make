import os
import shutil
import sys
import time
import json
import tempfile
import requests
import resource
import requests_mock
import pytest
import yaml

from sinol_make import util, configure_parsers
from sinol_make.helpers import paths
from tests import util as test_util
from tests.fixtures import create_package
from tests.commands.run import util as run_util


def test_file_diff():
    with tempfile.TemporaryDirectory() as tmpdir:
        a_file = os.path.join(tmpdir, 'a')
        b_file = os.path.join(tmpdir, 'b')

        open(a_file, 'w').write("1"
                                "2"
                                "3")

        open(b_file, 'w').write("1"
                                "2"
                                "3"
                                "4")

        assert util.file_diff(a_file, b_file) is False

        open(a_file, 'w').write("1\n")
        open(b_file, 'w').write("1        ")

        assert util.file_diff(a_file, b_file) is True

        open(a_file, 'w').write("1\n")
        open(b_file, 'w').write("1\n\n")

        assert util.file_diff(a_file, b_file) is False


def test_compare_versions():
    """
    Tests for compare_versions function
    """

    assert util.compare_versions('1.0.0', '1.0.0') == 0
    assert util.compare_versions('1.0.0', '1.0.1') == -1
    assert util.compare_versions('1.0.1', '1.0.0') == 1
    assert util.compare_versions('1.0.0', '1.1.0') == -1
    assert util.compare_versions('1.1.0', '1.0.0') == 1
    assert util.compare_versions('1.0.0', '2.0.0') == -1
    assert util.compare_versions('2.0.0', '1.0.0') == 1
    with pytest.raises(ValueError):
        util.compare_versions('1.0.0', '')
    with pytest.raises(ValueError):
        util.compare_versions('', '1.0.0')
    with pytest.raises(ValueError):
        util.compare_versions('1.0.0', 'abc')
    with pytest.raises(ValueError):
        util.compare_versions('abc', '1.0.0')


@requests_mock.Mocker(kw="mocker")
def test_check_version(**kwargs):
    """
    Tests for check_version function
    Simulates wrong responses and exceptions with requests-mock
    """
    mocker = kwargs["mocker"]

    importlib = util.import_importlib_resources()

    data_dir = importlib.files('sinol_make').joinpath("data")
    version_file = data_dir.joinpath("version")
    if not data_dir.is_dir():
        data_dir.mkdir()
    data_dir.chmod(0o777)
    if version_file.is_file():
        version_file.unlink()

    # Test correct request
    mocker.get("https://pypi.python.org/pypi/sinol-make/json", json={"info": {"version": "1.0.0"}})
    util.check_version()
    assert version_file.is_file()
    assert version_file.read_text() == "1.0.0"
    version_file.unlink()

    # Test wrong request
    mocker.get("https://pypi.python.org/pypi/sinol-make/json", status_code=404)
    util.check_version()
    assert not version_file.is_file()

    # Time out
    mocker.get("https://pypi.python.org/pypi/sinol-make/json", exc=requests.exceptions.ConnectTimeout)
    util.check_version()
    assert not version_file.is_file()


@pytest.mark.parametrize("create_package", [test_util.get_simple_package_path()], indirect=True)
def test_version_change(create_package):
    with open("config.yml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    old_expected_scores = config["sinol_expected_scores"]
    config["sinol_expected_scores"] = {'abc.cpp': {'points': 100, 'expected': {1: 'OK', 2: 'OK', 3: 'OK', 4: 'OK'}},
                                       'abc1.cpp': {'points': 75, 'expected': {1: 'OK', 2: 'OK', 3: 'OK', 4: 'WA'}},
                                       'abc2.cpp': {'points': 25, 'expected': {1: 'OK', 2: 'WA', 3: 'WA', 4: 'TL'}},
                                       'abc3.cpp': {'points': 25, 'expected': {1: 'OK', 2: 'WA', 3: 'WA', 4: 'ML'}},
                                       'abc4.cpp': {'points': 50, 'expected': {1: 'OK', 2: 'OK', 3: 'WA', 4: 'RE'}}}
    assert old_expected_scores == util.try_fix_config(config)["sinol_expected_scores"]
