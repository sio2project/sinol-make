import multiprocessing as mp
import os, glob
import argparse
import yaml

from sinol_make.structs.compiler_structs import Compilers
from ...util import *
from sinol_make.commands.run import Command
from sinol_make.helpers import compiler
from sinol_make.helpers import compile


def get_command(path = None):
    """
    Helper to get a command object with the constants set.
    """
    if path is None:
        path = get_simple_package_path()
    command = Command()
    command.set_constants()
    command.cpus = mp.cpu_count()
    command.compilers = Compilers(
        c_compiler_path=compiler.get_c_compiler_path(),
        cpp_compiler_path=compiler.get_cpp_compiler_path(),
        python_interpreter_path=compiler.get_python_interpreter_path(),
        java_compiler_path=compiler.get_java_compiler_path()
    )
    command.config = yaml.load(open(os.path.join(path, "config.yml"), "r"), Loader=yaml.FullLoader)
    command.checker = None
    command.failed_compilations = []
    set_default_args(command)
    return command


def set_default_args(command):
    command.args = argparse.Namespace(
        weak_compilation_flags=False,
    )
