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
    command.args = argparse.Namespace(cpus=1, compile_mode='default',
                                      cpp_compiler_path=compiler.get_cpp_compiler_path(),
                                      c_compiler_path=None, python_interpreter_path=None,
                                      java_compiler_path=None, export_ocen=False)
    command.task_type_cls = package_util.get_task_type_cls()
    return command


def test_get_generated_tests():
    """
    Test getting generated tests.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        command = _create_package(tmpdir, util.get_handwritten_package_path())
        command.generate_input_tests()
        assert set(command.get_generated_tests()) == {"1a", "2a"}

        command = _create_package(tmpdir, util.get_simple_package_path())
        command.generate_input_tests()
        assert set(command.get_generated_tests()) == {"1a", "2a", "3a", "4a"}


def test_copy_package_required_files():
    """
    Test function copy_package_required_files.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        res_dir = os.path.join(tmpdir, "res")
        os.mkdir(res_dir)
        command = _create_package(tmpdir, util.get_handwritten_package_path())
        command.generate_input_tests()
        command.copy_package_required_files(res_dir)

        assert_configs_equal(os.getcwd(), res_dir)
        assert_progs_equal(os.getcwd(), res_dir)

        assert set(os.listdir(os.path.join(res_dir, "in"))) == {"hwr0.in", "hwr0a.in"}
        assert set(os.listdir(os.path.join(res_dir, "out"))) == {"hwr0.out", "hwr0a.out"}

        shutil.rmtree(res_dir)
        os.mkdir(res_dir)
        command = _create_package(tmpdir, util.get_simple_package_path())
        command.generate_input_tests()
        command.copy_package_required_files(res_dir)

        assert_configs_equal(os.getcwd(), res_dir)
        assert_progs_equal(os.getcwd(), res_dir)

        assert set(os.listdir(os.path.join(res_dir, "in"))) == set()
        assert set(os.listdir(os.path.join(res_dir, "out"))) == set()


def test_create_makefile_in():
    """
    Test function create_makefile_in.
    """

    def _create_package(path):
        os.chdir(path)
        with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
        return get_command(), config

    with tempfile.TemporaryDirectory() as tmpdir:
        command, config = _create_package(util.get_handwritten_package_path())

        command.create_makefile_in(tmpdir, config)
        with open(os.path.join(tmpdir, "makefile.in"), "r") as makefile:
            lines = makefile.readlines()
            assert_makefile_in(lines, "hwr", config)

        for package in [util.get_library_package_path(), util.get_library_string_args_package_path()]:
            task_name = os.path.basename(package)
            command, config = _create_package(package)
            command.create_makefile_in(tmpdir, config)
            with open(os.path.join(tmpdir, "makefile.in"), "r") as makefile:
                lines = makefile.readlines()
                assert_makefile_in(lines, task_name, config)
