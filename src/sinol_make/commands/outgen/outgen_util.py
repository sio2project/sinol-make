import os
import signal
import subprocess
import sys

import argparse

from sinol_make import util
from sinol_make.helpers import package_util, compiler, compile


def get_correct_solution(task_id):
    """
    Returns path to correct solution for given task.
    :param task_id: task id, for example abc
    :return: path to correct solution or None if not found
    """
    correct_solution = package_util.get_files_matching_pattern(task_id, f'{task_id}.*')
    if len(correct_solution) == 0:
        util.exit_with_error(f'Correct solution for task {task_id} does not exist.')
    return correct_solution[0]


def compile_correct_solution(solution_path: str, args: argparse.Namespace, compilation_flags='default'):
    """
    Compiles correct solution and returns path to compiled executable.
    """
    compilers = compiler.verify_compilers(args, [solution_path])
    correct_solution_exe, compile_log_path = compile.compile_file(solution_path, package_util.get_executable(solution_path), compilers,
                                                                  compilation_flags)
    if correct_solution_exe is None:
        util.exit_with_error('Failed compilation of correct solution.',
                                  lambda: compile.print_compile_log(compile_log_path))
    else:
        print(util.info('Successfully compiled correct solution.'))

    return correct_solution_exe


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
