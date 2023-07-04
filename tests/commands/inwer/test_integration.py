import pytest

from sinol_make import configure_parsers
from sinol_make.commands.inwer import Command
from tests import util
from tests.fixtures import *


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_default(capsys, create_package):
    """
    Test `inwer` command with no parameters.
    """
    package_path = create_package
    util.create_ins(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["inwer"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 0

    out = capsys.readouterr().out
    assert "Verification successful." in out


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_specified_inwer(capsys, create_package):
    """
    Test `inwer` command with specified inwer.
    """
    package_path = create_package
    util.create_ins(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["inwer", "prog/werinwer.cpp"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 0

    out = capsys.readouterr().out
    assert "Verification successful." in out

    args = parser.parse_args(["inwer", "prog/werinwer2.cpp"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 1

    out = capsys.readouterr().out
    assert "Verification failed for tests: wer2a.in" in out


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_asserting_inwer(capsys, create_package):
    """
    Test `inwer` command with inwer that uses assert for verifying.
    """
    package_path = create_package
    util.create_ins(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["inwer", "prog/werinwer3.cpp"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 1

    out = capsys.readouterr().out
    assert "Verification failed for tests: wer2a.in" in out


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_flag_tests(capsys, create_package):
    """
    Test `inwer` command with --tests flag.
    """
    package_path = create_package
    util.create_ins(package_path)
    parser = configure_parsers()
    args = parser.parse_args(["inwer", "prog/werinwer.cpp", "--tests", "in/wer2a.in"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 0

    out = capsys.readouterr().out
    assert "Verification successful." in out
    assert "wer2a.in" in out
    assert "wer1a.in" not in out

    args = parser.parse_args(["inwer", "prog/werinwer2.cpp", "--tests", "in/wer2a.in", "in/wer1a.in"])
    command = Command()

    with pytest.raises(SystemExit) as e:
        command.run(args)

    assert e.type == SystemExit
    assert e.value.code == 1

    out = capsys.readouterr().out
    assert "Verification failed for tests: wer2a.in" in out
    assert "wer1a.in" in out
    assert "wer2a.in" in out
    assert "wer3a.in" not in out
