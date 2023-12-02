import os
import glob
import subprocess

from sinol_make.compilers.CompilersManager import CompilerManager
from sinol_make.programs.ingen import Ingen
from sinol_make.programs.solution import Solution
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest
from sinol_make.timetools.TimeToolManager import TimeToolManager
from sinol_make.executor import Executor
from sinol_make import util, configure_parsers
from sinol_make.helpers import paths, package_util


def run(cls, arguments=None):
    if arguments is None:
        arguments = []
    if isinstance(arguments, str):
        arguments = arguments.split()
    parser = get_parser()
    args = parser.parse_args(arguments)
    command = get_command(cls)
    command.run(args)
    return command


def get_parser():
    timetool_manager = TimeToolManager()
    executor = Executor(timetool_manager)
    commands = util.get_commands(timetool_manager, executor)
    return configure_parsers(commands)


def get_command(cls):
    timetool_manager = TimeToolManager()
    executor = Executor(timetool_manager)
    return cls(timetool_manager, executor)


def get_doc_command():
    from sinol_make.commands.doc import Command
    return get_command(Command)


def get_export_command():
    from sinol_make.commands.export import Command
    return get_command(Command)


def get_gen_command():
    from sinol_make.commands.gen import Command
    return get_command(Command)


def get_inwer_command():
    from sinol_make.commands.inwer import Command
    return get_command(Command)


def get_run_command():
    from sinol_make.commands.run import Command
    return get_command(Command)


def get_simple_package_path():
    """Get path to simple package (/tests/packages/abc)"""
    return os.path.join(os.path.dirname(__file__), "packages", "abc")


def get_verify_status_package_path():
    """
    Get path to package for veryfing status order (/test/packages/vso)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "vso")


def get_checker_package_path():
    """
    Get path to package for checker (/test/packages/chk)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "chk")


def get_library_package_path():
    """
    Get path to package with library command (/test/packages/lib)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "lib")


def get_library_string_args_package_path():
    """
    Get path to package with library command with string extra_compilation_args (/test/packages/lsa)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "lsa")


def get_weak_compilation_flags_package_path():
    """
    Get path to package for testing weak compilation flags (/test/packages/wcf)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "wcf")


def get_inwer_package_path():
    """
    Get path to package for inwer command (/test/packages/wer)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "wer")


def get_shell_ingen_pack_path():
    """
    Get path to package for testing shell ingen (/test/packages/gen)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "gen")


def get_limits_package_path():
    """
    Get path to package with `time_limits` and `memory_limits` present in config (/test/packages/lim)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "lim")


def get_handwritten_package_path():
    """
    Get path to package with handwritten tests (/test/packages/hw)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "hwr")


def get_stack_size_package_path():
    """
    Get path to package for testing of changing stack size (/test/packages/stc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "stc")


def get_override_limits_package_path():
    """
    Get path to package with `override_limits` present in config (/test/packages/ovl)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "ovl")


def get_doc_package_path():
    """
    Get path to package for testing `doc` command (/test/packages/doc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "doc")


def get_long_name_package_path():
    """
    Get path to package with long name (/test/packages/long_package_name)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "long_package_name")


def get_undocumented_options_package_path():
    """
    Get path to package with undocumented options in config.yml (/test/packages/undoc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "undocumented_options")


def get_example_tests_package_path():
    """
    Get path to package with only example tests (/tests/packages/example_tests)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "example_tests")


def get_icpc_package_path():
    """
    Get path to package with icpc contest type (/tests/packages/icpc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "icpc")


def get_long_solution_names_package():
    """
    Get path to package with long solution names (/tests/packages/long_solution_names)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "long_solution_names")


def get_large_output_package_path():
    """
    Get path to package with large output (/tests/packages/large_output)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "large_output")


def _create_ins(package_path, task_id, timetool_manager, executor, compiler_manager):
    """
    Create .in files for package.
    """
    try:
        ingen = Ingen(executor, compiler_manager, task_id)
    except FileNotFoundError:
        return
    exe, _ = ingen.compile()
    assert exe is not None
    ingen.run()
    os.chdir(package_path)


def create_ins(package_path, task_id):
    timetool_manager = TimeToolManager()
    executor = Executor(timetool_manager)
    compiler_manager = CompilerManager(None)
    os.chdir(package_path)
    _create_ins(package_path, task_id, timetool_manager, executor, compiler_manager)


def _create_outs(package_path, task_id, timetool_manager, executor, compiler_manager):
    """
    Create .out files for package.
    """
    solution = Solution(executor, compiler_manager, task_id)
    exe, _ = solution.compile()
    assert exe is not None
    for test in InputTest.get_all(task_id):
        output_test = OutputTest(task_id, os.path.splitext(test.basename)[0] + ".out", exists=False)
        with test.open("r") as in_file, output_test.open("w") as out_file:
            solution.run(stdin=in_file, stdout=out_file)


def create_outs(package_path, task_id):
    timetool_manager = TimeToolManager()
    executor = Executor(timetool_manager)
    compiler_manager = CompilerManager(None)
    os.chdir(package_path)
    _create_outs(package_path, task_id, timetool_manager, executor, compiler_manager)


def create_ins_outs(package_path):
    """
    Create .in and .out files for package.
    """
    timetool_manager = TimeToolManager()
    executor = Executor(timetool_manager)
    compiler_manager = CompilerManager(None)
    os.chdir(package_path)
    task_id = package_util.get_task_id()
    _create_ins(package_path, task_id, timetool_manager, executor, compiler_manager)
    has_lib = package_util.any_files_matching_pattern(task_id, f"{task_id}lib.*")
    if not has_lib:
        _create_outs(package_path, task_id, timetool_manager, executor, compiler_manager)
