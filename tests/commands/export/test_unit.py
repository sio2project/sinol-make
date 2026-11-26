import yaml
import shutil
import tempfile

import os
from tests import util
from .util import *
from sinol_make.commands.ingen.ingen_util import generate_input_tests, get_generated_tests
from sinol_make.commands.export import Command
from sinol_make.helpers import paths

def _create_package(tmpdir, path):
    package_path = os.path.join(tmpdir, os.path.basename(path))
    shutil.copytree(path, package_path)
    os.chdir(package_path)
    command = get_command()
    util.create_ins_outs(package_path)
    command.args = argparse.Namespace(cpus=1, compile_mode='default',
                                      cpp_compiler_path=compiler.get_cpp_compiler_path(),
                                      c_compiler_path=None, python_interpreter_path=None,
                                      java_compiler_path=None, rust_compiler_path=None,
                                      export_ocen=False, sanitize='no')
    command.task_type_cls = package_util.get_task_type_cls()
    return command


def test_get_generated_tests():
    """
    Test getting generated tests.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        command = _create_package(tmpdir, util.get_handwritten_package_path())
        target_dir = paths.get_cache_path('export', 'tests')
        generate_input_tests(command.task_id, command.args, target_dir)
        assert set(get_generated_tests(command.task_id, target_dir)) == {"1a", "2a"}

        command = _create_package(tmpdir, util.get_simple_package_path())
        target_dir = paths.get_cache_path('export', 'tests')
        generate_input_tests(command.task_id, command.args, target_dir)
        assert set(get_generated_tests(command.task_id, target_dir)) == {"1a", "2a", "3a", "4a"}



def test_copy_package_required_files():
    """
    Test function copy_package_required_files.
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        res_dir = os.path.join(tmpdir, "res")
        os.mkdir(res_dir)
        command = _create_package(tmpdir, util.get_handwritten_package_path())
        target_dir = paths.get_cache_path('export', 'tests')
        generate_input_tests(command.task_id, command.args, target_dir)
        command.copy_package_required_files(res_dir)

        assert_configs_equal(os.getcwd(), res_dir)
        assert_progs_equal(os.getcwd(), res_dir)

        assert set(os.listdir(os.path.join(res_dir, "in"))) == {"hwr0.in", "hwr0a.in"}
        assert set(os.listdir(os.path.join(res_dir, "out"))) == {"hwr0.out", "hwr0a.out"}

        shutil.rmtree(res_dir)
        os.mkdir(res_dir)
        command = _create_package(tmpdir, util.get_simple_package_path())
        target_dir = paths.get_cache_path('export', 'tests')
        generate_input_tests(command.task_id, command.args, target_dir)
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


def test_clear_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, "prog"))
        os.makedirs(os.path.join(tmpdir, "doc"))
        os.makedirs(os.path.join(tmpdir, "prog", "__pycache__"))

        with open(os.path.join(tmpdir, "prog", "foo.bak"), "w"):
            pass

        with open(os.path.join(tmpdir, "prog", "foo.cpp"), "w"):
            pass

        with open(os.path.join(tmpdir, "doc", "foo.log"), "w"):
            pass

        command = Command()

        config = {
            "sinol_cleanup_patterns": [
                "*.bak",
                "__pycache__/",
            ],
        }

        command.clear_files(tmpdir, config)

        assert not os.path.exists(
            os.path.join(tmpdir, "prog", "foo.bak")
        )

        assert not os.path.exists(
            os.path.join(tmpdir, "prog", "__pycache__")
        )

        assert os.path.exists(
            os.path.join(tmpdir, "prog", "foo.cpp")
        )

        # Default export cleanup behavior.
        assert not os.path.exists(
            os.path.join(tmpdir, "doc", "foo.log")
        )
