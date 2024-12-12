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


@requests_mock.Mocker(kw="mocker")
def test_check_version(**kwargs):
    """
    Tests for check_version function
    Simulates wrong responses and exceptions with requests-mock
    """
    mocker = kwargs["mocker"]

    def create_response(version):
        return {"releases": {version: "something"}}

    mocker.get("https://pypi.python.org/pypi/sinol-make/json", json=create_response("1.0.0.dev2"))
    util.check_version()
    version = util.check_for_updates("1.0.0.dev1", False)
    assert version == "1.0.0.dev2"
    assert util.is_dev(version)

    mocker.get("https://pypi.python.org/pypi/sinol-make/json", json=create_response("1.0.0"))
    util.check_version()
    version = util.check_for_updates("1.0.0.dev1", False)
    assert version == "1.0.0"
    assert not util.is_dev(version)

    mocker.get("https://pypi.python.org/pypi/sinol-make/json", json=create_response("2.0.0.dev1"))
    util.check_version()
    version = util.check_for_updates("1.0.0", False)
    assert version is None

    mocker.get("https://pypi.python.org/pypi/sinol-make/json", json=create_response("1.0.1"))
    util.check_version()
    version = util.check_for_updates("1.0.0", False)
    assert version == "1.0.1"
    assert not util.is_dev(version)

    importlib = util.import_importlib_resources()

    data_dir = importlib.files('sinol_make').joinpath("data")
    version_file = data_dir.joinpath("version")
    if not data_dir.is_dir():
        data_dir.mkdir()
    data_dir.chmod(0o777)
    if version_file.is_file():
        version_file.unlink()

    # Test correct request
    mocker.get("https://pypi.python.org/pypi/sinol-make/json", json=create_response(("1.0.0")))
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


def test_saving_config_with_unicode(create_package):
    config_path = os.path.join(create_package, "config.yml")
    polish_title = "Zadanie ęĘóÓąĄśŚżŻźŹćĆńŃ"
    polish_title_yaml = "title: " + polish_title

    def read_config_lines():
        with open(config_path, "r") as config_file:
            return config_file.read().split('\n')

    config_text = '\n'.join([polish_title_yaml] + read_config_lines()[1:])
    with open(config_path, "w") as config_file:
        config_file.write(config_text)

    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    assert config['title'] == polish_title
    util.save_config(config)
    assert read_config_lines()[0] == polish_title_yaml
