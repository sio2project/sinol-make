import pytest
import yaml

from tests import util
from tests.fixtures import create_package
from sinol_make.util import make_version_changes
import sinol_make


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_version_change(create_package):
    orig_version = sinol_make.__version__
    sinol_make.__version__ = "1.5.9"

    with open("config.yml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    old_expected_scores = config["sinol_expected_scores"]
    config["sinol_expected_scores"] = {'abc.cpp': {'points': 100, 'expected': {1: 'OK', 2: 'OK', 3: 'OK', 4: 'OK'}},
                                       'abc1.cpp': {'points': 75, 'expected': {1: 'OK', 2: 'OK', 3: 'OK', 4: 'WA'}},
                                       'abc2.cpp': {'points': 25, 'expected': {1: 'OK', 2: 'WA', 3: 'WA', 4: 'TL'}},
                                       'abc3.cpp': {'points': 25, 'expected': {1: 'OK', 2: 'WA', 3: 'WA', 4: 'ML'}},
                                       'abc4.cpp': {'points': 50, 'expected': {1: 'OK', 2: 'OK', 3: 'WA', 4: 'RE'}}}
    with open("config.yml", "w") as config_file:
        yaml.dump(config, config_file)

    make_version_changes()

    with open("config.yml", "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    assert config["sinol_expected_scores"] == old_expected_scores
    sinol_make.__version__ = orig_version
