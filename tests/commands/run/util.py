import multiprocessing as mp
import os, glob

import yaml
from ...util import *
from sinol_make.commands.run import Command
from sinol_make.helpers import compiler
from sinol_make.helpers import compile

def get_command(path = None):
    """
    Helper to get a command object with the constants set.
    Changes dir to simple test package.
    """
    if path is None:
        path = get_simple_package_path()
    command = Command()
    command.set_constants()
    command.cpus = mp.cpu_count()
    command.compilers = {
        'c_compiler_path': compiler.get_c_compiler_path(),
        'cpp_compiler_path': compiler.get_cpp_compiler_path(),
        'python_interpreter_path': compiler.get_python_interpreter_path(),
        'java_compiler_path': compiler.get_java_compiler_path()
    }
    command.config = yaml.load(open(os.path.join(path, "config.yml"), "r"), Loader=yaml.FullLoader)
    command.checker = None
    return command

def create_ins(package_path):
    """
    Create .in files for package.
    """
    ingen = glob.glob(os.path.join(package_path, "prog", "*ingen.*"))[0]
    ingen_executable = os.path.join(package_path, "cache", "executables", "ingen.e")
    os.makedirs(os.path.join(package_path, "cache", "executables"), exist_ok=True)
    assert compile.compile(ingen, ingen_executable)
    os.chdir(os.path.join(package_path, "in"))
    os.system("../cache/executables/ingen.e")
    os.chdir(package_path)


def create_outs(package_path):
    """
    Create .out files for package.
    """
    solution = glob.glob(os.path.join(package_path, "prog", "???.*"))[0]
    solution_executable = os.path.join(package_path, "cache", "executables", "solution.e")
    os.makedirs(os.path.join(package_path, "cache", "executables"), exist_ok=True)
    assert compile.compile(solution, solution_executable)
    os.chdir(os.path.join(package_path, "in"))
    for file in glob.glob("*.in"):
        os.system(f'{os.path.join(package_path, "cache", "executables", "solution.e")} < {file} > ../out/{file.replace(".in", ".out")}')
    os.chdir(package_path)


def create_ins_outs(package_path):
    """
    Create .in and .out files for package.
    """
    create_ins(package_path)
    checker = glob.glob(os.path.join(package_path, "prog", "???chk.*"))
    if len(checker) == 0:
        create_outs(package_path)
