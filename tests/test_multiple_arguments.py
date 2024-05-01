import pytest
import subprocess

from tests.fixtures import create_package
from tests import util


def run(args):
    print("Running with args:", args)
    p = subprocess.run(args, shell=True)
    assert p.returncode == 0


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_simple_package(create_package):
    run("sinol-make gen run")
    run("sinol-make gen prog/abcingen.cpp run --tests abc1a.in")
    run("sinol-make run --tests abc1a.in run --tests abc1a.in abc2a.in ingen prog/abcingen.cpp")
    run("sinol-make gen run export --no-statement")


@pytest.mark.parametrize("create_package", [util.get_inwer_package_path()], indirect=True)
def test_inwer_package(create_package):
    run("sinol-make gen inwer run")
    run("sinol-make ingen prog/weringen.cpp inwer prog/werinwer.cpp --tests wer1a.in run --tests wer2a.in")
    run("sinol-make ingen inwer run export --no-statement")


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_doc_package(create_package):
    run("sinol-make doc doc/doczad.tex export")
