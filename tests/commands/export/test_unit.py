import os
import yaml
import shutil
import tempfile

from tests import util
from .util import *


def _create_package(tmpdir, path):
    package_path = os.path.join(tmpdir, os.path.basename(path))
    shutil.copytree(path, package_path)
    os.chdir(package_path)
    command = get_command()
    util.create_ins_outs(package_path)
    return command


def test_get_generated_tests():
    """
    Test getting generated tests.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        command = _create_package(tmpdir, util.get_handwritten_package_path())
        assert set(command.get_generated_tests()) == {"1a", "2a"}

        command = _create_package(tmpdir, util.get_simple_package_path())
        assert set(command.get_generated_tests()) == {"1a", "2a", "3a", "4a"}


def test_copy_files():
    """
    Test function copy_files.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        res_dir = os.path.join(tmpdir, "res")
        os.mkdir(res_dir)
        command = _create_package(tmpdir, util.get_handwritten_package_path())
        command.copy_files(res_dir)

        assert_configs_equal(os.getcwd(), res_dir)
        assert_progs_equal(os.getcwd(), res_dir)

        assert set(os.listdir(os.path.join(res_dir, "in"))) == {"hwr0.in", "hwr0a.in"}
        assert set(os.listdir(os.path.join(res_dir, "out"))) == {"hwr0.out", "hwr0a.out"}

        shutil.rmtree(res_dir)
        os.mkdir(res_dir)
        command = _create_package(tmpdir, util.get_simple_package_path())
        command.copy_files(res_dir)

        assert_configs_equal(os.getcwd(), res_dir)
        assert_progs_equal(os.getcwd(), res_dir)

        assert set(os.listdir(os.path.join(res_dir, "in"))) == set()
        assert set(os.listdir(os.path.join(res_dir, "out"))) == set()


def test_create_files():
    """
    Test function create_files.
    """

    def _create_package(path):
        os.chdir(path)
        with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
        return get_command(), config

    with tempfile.TemporaryDirectory() as tmpdir:
        command, config = _create_package(util.get_handwritten_package_path())

        command.create_files(tmpdir, config)
        with open(os.path.join(tmpdir, "makefile.in"), "r") as makefile:
            lines = makefile.readlines()
            assert_makefile_in(lines, "hwr", config)

        command, config = _create_package(util.get_library_package_path())
        command.create_files(tmpdir, config)
        with open(os.path.join(tmpdir, "makefile.in"), "r") as makefile:
            lines = makefile.readlines()
            assert_makefile_in(lines, "lib", config)


def test_ocen_gen_conf():
    """
    Test function ocen_gen_conf.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(util.get_simple_package_path())
        command = get_command()

        command.ocen_gen_conf(tmpdir, {"0", "1ocen", "2ocen"})
        with open(os.path.join(tmpdir, "oi.conf"), "r") as conf:
            assert conf.read() == f'TASKS="abc"\n' \
                                  'TESTS_abc="0 1ocen 2ocen"\n' \
                                  'HARD_TIMELIMIT=60    # limit czasu na wykonanie pod oitimetool (zwroc  uwage,\n' \
                                  '                     # ze nie ma to nic wspolnego z wynikiem oitimetool dla Twojego programu)\n' \
                                  'MEMLIMIT=1000000   # limit wykorzysztania pamieci przez program oraz oitimetool (KiB)\n' \
                                  'SRCLIMIT=100     # limit na rozmiar pliku zrodlowego (KiB)\n' \
                                  'EXELIMIT=10240   # limit na rozmiar pliku wykonywalnego (KiB) = 10MB\n'
