import os
import shutil
from linecache import cache

import pytest

from sinol_make import configure_parsers
from sinol_make import util as sm_util
from sinol_make.commands.verify import Command
from sinol_make.helpers import package_util, paths, func_cache, cache
from tests import util
from tests.fixtures import create_package


def run(args=None):
    if args is None:
        args = []
    parser = configure_parsers()
    command = Command()
    args = parser.parse_args(['verify'] + args)
    command.run(args)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_inwer_package_path()],
                         indirect=True)
def test_simple_package(capsys, create_package):
    """
    Test if simple package runs successfully.
    """
    run()


@pytest.mark.parametrize("create_package", [util.get_stresstest_package_path()], indirect=True)
def test_stresstest_package(capsys, create_package):
    """
    Test if stresstest.sh script runs. Then check if after failing the stresstest.sh script, the verify command
    will fail as well.
    """
    run()
    out = capsys.readouterr().out
    assert "Running stress tests" in out

    stresstest_path = os.path.join(create_package, "prog", "strstresstest.sh")
    with open(stresstest_path, "r") as f:
        code = f.read()
    with open(stresstest_path, "w") as f:
        f.write(code.replace("exit 0", "exit 1"))

    with pytest.raises(SystemExit) as e:
        run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Running stress tests" in out
    assert "Stress tests failed." in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_missing_extra_files(capsys, create_package):
    """
    Test if missing extra files will cause the verify command to fail.
    """
    config = package_util.get_config()
    config["extra_compilation_files"] = ["missing_file"]
    sm_util.save_config(config)
    with pytest.raises(SystemExit) as e:
        run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Extra compilation file `missing_file` does not exist." in out

    del config["extra_compilation_files"]
    config["extra_execution_files"] = {"cpp": ["missing_file"]}
    sm_util.save_config(config)
    with pytest.raises(SystemExit) as e:
        run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Extra execution file `missing_file` for language `cpp` does not exist." in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_invalid_scores(capsys, create_package):
    """
    Test if invalid scores will cause the verify command to fail.
    """
    config = package_util.get_config()
    scores = config["scores"]
    config["scores"] = {1: 100}
    sm_util.save_config(config)
    with pytest.raises(SystemExit) as e:
        run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Score for group '2' not found." in out

    config["scores"] = scores
    config["scores"][20] = 0
    sm_util.save_config(config)
    with pytest.raises(SystemExit) as e:
        run()
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Score for group '20' found in config" in out


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_scores_not_100(capsys, create_package):
    """
    Test if scores not adding up to 100 will cause the verify command to fail if contest type is OI or OIJ.
    """
    config = package_util.get_config()
    config["scores"][1] -= 1
    sm_util.save_config(config)
    for contest_type in ["oi", "oij"]:
        if os.path.exists(paths.get_cache_path()):
            shutil.rmtree(paths.get_cache_path())
            cache.create_cache_dirs()
        config = package_util.get_config()
        config["sinol_contest_type"] = contest_type
        sm_util.save_config(config)
        with pytest.raises(SystemExit) as e:
            run()
        assert e.value.code == 1
        out = capsys.readouterr().out
        assert "Total score in config is 99, but should be 100." in out


@pytest.mark.parametrize("create_package", [util.get_dlazaw_package()], indirect=True)
def test_expected_contest_and_no_scores(capsys, create_package):
    """
    Test if --expected-contest-type flag works,
    and if contest type is OI or OIJ and there are no scores in config.yml, the verify command will fail.
    """
    config = package_util.get_config()
    with pytest.raises(SystemExit) as e:
        run(["--expected-contest-type", "icpc"])
    assert e.value.code == 1
    out = capsys.readouterr().out
    assert "Invalid contest type 'oi'. Expected 'icpc'." in out

    del config["scores"]
    for contest_type in ["oi", "oij"]:
        func_cache.clear_cache()
        config["sinol_contest_type"] = contest_type
        sm_util.save_config(config)
        with pytest.raises(SystemExit) as e:
            run(["--expected-contest-type", contest_type])
        assert e.value.code == 1
        out = capsys.readouterr().out
        assert "Scores are not defined in config.yml." in out
