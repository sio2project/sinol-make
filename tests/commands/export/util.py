import os
import argparse

from sinol_make.helpers import compiler
from sinol_make.commands.export import Command
from sinol_make.helpers import package_util


def get_command():
    command = Command()
    command.task_id = package_util.get_task_id()
    command.args = argparse.Namespace(
        compile_mode='default',
        c_compiler_path=compiler.get_c_compiler_path(),
        cpp_compiler_path=compiler.get_cpp_compiler_path(),
        python_interpreter_path=compiler.get_python_interpreter_path(),
        java_compiler_path=compiler.get_java_compiler_path(),
    )
    command.export_dir = os.path.join(os.getcwd(), "export")
    if not os.path.exists(command.export_dir):
        os.mkdir(command.export_dir)

    return command


def assert_configs_equal(path1, path2):
    with open(os.path.join(path1, "config.yml"), "r") as config_orig, \
            open(os.path.join(path2, "config.yml"), "r") as config_res:
        assert config_orig.read() == config_res.read()


def assert_progs_equal(path1, path2):
    assert set(os.listdir(os.path.join(path1, "prog"))) == \
           set(os.listdir(os.path.join(path2, "prog")))


def assert_makefile_in(lines, task_id, config):
    """
    Asserts that the `makefile.in` is correct.
    :param lines: Lines of the makefile.in
    :param task_id: Task id
    :param config: Config dict
    """
    def _get_value_from_key(key, seperator):
        for line in lines:
            split = line.split(seperator)
            if split[0].strip() == key:
                return split[1].strip().strip('\n')
        return None

    assert _get_value_from_key("ID", "=") == task_id
    assert _get_value_from_key("TIMELIMIT", "=") == str(config["time_limit"])
    assert _get_value_from_key("SLOW_TIMELIMIT", "=") == str(4 * config["time_limit"])
    assert _get_value_from_key("MEMLIMIT", "=") == str(config["memory_limit"])

    cxx_flags = '-std=c++20'
    c_flags = '-std=gnu99'
    def format_multiple_arguments(obj):
        if isinstance(obj, str):
            return obj
        return ' '.join(obj)

    if 'extra_compilation_args' in config:
        if 'cpp' in config['extra_compilation_args']:
            cxx_flags += ' ' + format_multiple_arguments(config['extra_compilation_args']['cpp'])
        if 'c' in config['extra_compilation_args']:
            c_flags += ' ' + format_multiple_arguments(config['extra_compilation_args']['c'])

    assert _get_value_from_key("CXXFLAGS", "+=") == cxx_flags
    assert _get_value_from_key("CFLAGS", "+=") == c_flags
