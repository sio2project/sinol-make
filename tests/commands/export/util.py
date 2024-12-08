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
    def _get_values_from_key(key, separator):
        for line in lines:
            split = line.split(separator)
            if split[0].strip() == key:
                yield split[1].strip().strip('\n')

    def _get_value_from_key(key, separator):
        value, = _get_values_from_key(key, separator)
        return value

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

    cxx_flags_vals = list(_get_values_from_key("CXXFLAGS", "+="))
    c_flags_vals = list(_get_values_from_key("CFLAGS", "+="))
    assert cxx_flags_vals[0] == cxx_flags
    assert c_flags_vals[0] == c_flags
    if 'extra_compilation_args' in config:
        # extra C/CXX args should be appended after ingen/inwer/chk targets
        if 'cpp' in config['extra_compilation_args']:
            extra_cxx_args = format_multiple_arguments(config['extra_compilation_args']['cpp'])
            assert cxx_flags_vals[1] == extra_cxx_args
        if 'c' in config['extra_compilation_args']:
            c_flags += ' ' + format_multiple_arguments(config['extra_compilation_args']['c'])
            assert c_flags_vals[1] == extra_c_args
