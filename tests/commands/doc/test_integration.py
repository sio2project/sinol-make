import os
import glob
import pytest

from sinol_make import configure_parsers
from sinol_make.commands.doc import Command
from sinol_make.helpers import paths
from tests.fixtures import create_package
from tests import util


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_simple(capsys, create_package):
    """
    Test `doc` command with no parameters.
    """
    parser = configure_parsers()
    args = parser.parse_args(["doc"])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert "Compilation was successful for all files." in out

    for pattern in command.LOG_PATTERNS:
        assert glob.glob(os.path.join(os.getcwd(), 'doc', pattern)) == []


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_argument(capsys, create_package):
    """
    Test `doc` command with specified file.
    """
    parser = configure_parsers()
    args = parser.parse_args(["doc", "doc/doczad.tex"])
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert "Compilation was successful for all files." in out
    assert "pdflatex" in out # In auto mode this command will use pdflatex

    logs_exist = False
    logs_dir = paths.get_cache_path('doc_logs')
    for pattern in command.LOG_PATTERNS:
        assert glob.glob(os.path.join(os.getcwd(), 'doc', pattern)) == []
        logs_exist = logs_exist | (glob.glob(os.path.join(logs_dir, pattern)) != [])
    assert logs_exist

def run_doc(capsys, command_args, expected, not_expected):
    """
    Run doc command
    """
    parser = configure_parsers()
    args = parser.parse_args(command_args)
    command = Command()
    command.run(args)
    out = capsys.readouterr().out
    assert "Compilation was successful for all files." in out
    assert expected in out 
    assert not_expected not in out 

@pytest.mark.parametrize("create_package", [util.get_ps_doc_package_path()], indirect=True)
def test_ps_images(capsys, create_package):
    """
    Test `doc` command with ps images.
    """
    run_doc(
        capsys=capsys,
        command_args=["doc"],
        expected="latex to dvi", # In auto mode this command should use latex and dvipdf
        not_expected="pdflatex" # and shouldn't use pdflatex for any compilation
    )


@pytest.mark.parametrize("create_package", [util.get_ps_doc_package_path()], indirect=True)
def test_compilation_mode(capsys, create_package):
    """
    Test `doc` with compilation mode directly specified.
    """
    run_doc(
        capsys=capsys,
        command_args=["doc", "doc/doczad.tex", "--latex-compiler", "pdflatex"],
        expected="pdflatex",
        not_expected="latex to dvi"
    )


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_compilation_mode_2(capsys, create_package):
    """
    Test `doc` with compilation mode directly specified.
    """
    run_doc(
        capsys=capsys,
        command_args=["doc", "doc/doczad.tex", "--latex-compiler", "latex_dvi"],
        expected="latex to dvi",
        not_expected="pdflatex"
    )


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_compilation_mode_3(capsys, create_package):
    """
    Test `doc` with compilation mode directly specified.
    """
    run_doc(
        capsys=capsys,
        command_args=["doc", "doc/doczad.tex", "--latex-compiler", "lualatex"],
        expected="lualatex",
        not_expected="pdflatex"
    )


@pytest.mark.parametrize("create_package", [util.get_luadoc_package_path()], indirect=True)
def test_compilation_mode_config(capsys, create_package):
    """
    Test `doc` with compilation mode specified in the configuration file.
    """
    run_doc(
        capsys=capsys,
        command_args=["doc"],
        expected="lualatex",
        not_expected="pdflatex"
    )


@pytest.mark.parametrize("create_package", [util.get_luadoc_package_path()], indirect=True)
def test_compilation_mode_config_override(capsys, create_package):
    """
    Test `doc` with compilation mode specified in the configuration file, and
    then overridden on the command-line.
    """
    run_doc(
        capsys=capsys,
        command_args=["doc", "--latex-compiler", "pdflatex"],
        expected="pdflatex",
        not_expected="lualatex"
    )
