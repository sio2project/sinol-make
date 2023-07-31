import glob
import os

import argparse
import signal
import subprocess
import sys

from sinol_make import util
from sinol_make.helpers import compiler, package_util, compile


def get_ingen(task_id=None, ingen_path=None):
    """
    Find ingen source file in `prog/` directory.
    If `ingen_path` is specified, then it will be used (if exists).
    :param task_id: task id, for example abc. If None, then
                    will return any ingen matching "*ingen.*"
    :param ingen_path: path to ingen source file
    :return: path to ingen source file or None if not found
    """

    if ingen_path is not None:
        if os.path.exists(ingen_path):
            return ingen_path
        else:
            return None

    if task_id is None:
        task_id = '*'
    ingen = glob.glob(os.path.join(os.getcwd(), 'prog', task_id + 'ingen.*'))
    if len(ingen) == 0:
        return None

    # Sio2 first chooses shell scripts, then non-shell source codes.
    if os.path.splitext(ingen[0])[1] == '.sh' and len(ingen) > 1:
        return ingen[1]
    else:
        return ingen[0]


def compile_ingen(ingen_path: str, args: argparse.Namespace, weak_compilation_flags=False):
    """
    Compiles ingen and returns path to compiled executable and path to compile log.
    """
    compilers = compiler.verify_compilers(args, [ingen_path])
    return compile.compile_file(ingen_path, package_util.get_executable(ingen_path), compilers, weak_compilation_flags)


def get_correct_solution(task_id):
    """
    Returns path to correct solution for given task.
    :param task_id: task id, for example abc
    :return: path to correct solution or None if not found
    """
    correct_solution = glob.glob(os.path.join(os.getcwd(), 'prog', task_id + '.*'))
    if len(correct_solution) == 0:
        return None
    return correct_solution[0]


def compile_correct_solution(solution_path: str, args: argparse.Namespace, weak_compilation_flags=False):
    """
    Compiles correct solution and returns path to compiled executable and path to compile log.
    """
    compilers = compiler.verify_compilers(args, [solution_path])
    return compile.compile_file(solution_path, package_util.get_executable(solution_path), compilers,
                                weak_compilation_flags)


def run_ingen(ingen_exe):
    """
    Runs ingen and generates all input files.
    :param ingen_exe: path to ingen executable
    :return: True if ingen was successful, False otherwise
    """
    shell = os.path.splitext(ingen_exe)[1] == '.sh'

    process = subprocess.Popen([ingen_exe], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               cwd=os.path.join(os.getcwd(), 'in'), shell=shell)
    while process.poll() is None:
        line = process.stdout.readline()
        if line:
            print(line.decode('utf-8'), end='')
    line = process.stdout.read().decode('utf-8').strip()
    if line:
        print(process.stdout.read().decode('utf-8'), end='')
    exit_code = process.returncode

    return exit_code == 0


def generate_output(arguments):
    """
    Generates output file for given input file.
    :param arguments: arguments for output generation (type OutputGenerationArguments)
    :return: True if the output was successfully generated, False otherwise
    """
    input_test = arguments.input_test
    output_test = arguments.output_test
    correct_solution_exe = arguments.correct_solution_exe

    input_file = open(input_test, 'r')
    output_file = open(output_test, 'w')
    process = subprocess.Popen([correct_solution_exe], stdin=input_file, stdout=output_file, preexec_fn=os.setsid)
    previous_sigint_handler = signal.getsignal(signal.SIGINT)

    def sigint_handler(signum, frame):
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        sys.exit(1)
    signal.signal(signal.SIGINT, sigint_handler)

    process.wait()
    signal.signal(signal.SIGINT, previous_sigint_handler)
    exit_code = process.returncode
    input_file.close()
    output_file.close()

    return exit_code == 0