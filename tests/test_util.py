import os
import sys
import time
import json
import tempfile
import requests
import requests_mock
import importlib.resources

import pytest

from sinol_make import util


@pytest.mark.github_runner
def test_install_oiejq():
    if sys.platform != 'linux':
        return

    if util.check_oiejq():
        os.remove(sys.path.expanduser('~/.local/bin/oiejq'))
        assert not util.check_oiejq()

    assert util.install_oiejq()


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

    data_dir = importlib.resources.files('sinol_make').joinpath("data")
    version_file = data_dir.joinpath("version")
    if not data_dir.is_dir():
        data_dir.mkdir()

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
