import glob
import os
import stat
import argparse
import signal
import subprocess
import sys

from sinol_make import util
from sinol_make.helpers import compiler, package_util, compile


def ingen_exists(task_id):
    """
    Checks if ingen source file exists.
    :param task_id: task id, for example abc
    :return: True if exists, False otherwise
    """
    return package_util.any_files_matching_pattern(task_id, f'{task_id}ingen.*')


def get_ingen(task_id, ingen_path=None):
    """
    Find ingen source file in `prog/` directory.
    If `ingen_path` is specified, then it will be used (if exists).
    :param task_id: task id, for example abc.
    :param ingen_path: path to ingen source file
    :return: path to ingen source file or None if not found
    """

    if ingen_path is not None:
        if os.path.exists(ingen_path):
            return ingen_path
        else:
            util.exit_with_error(f'Ingen source file {ingen_path} does not exist.')

    ingen = package_util.get_files_matching_pattern(task_id, f'{task_id}ingen.*')
    if len(ingen) == 0:
        util.exit_with_error(f'Ingen source file for task {task_id} does not exist.')

    # Sio2 first chooses shell scripts, then non-shell source codes.
    correct_ingen = None
    for i in ingen:
        if os.path.splitext(i)[1] == '.sh':
            correct_ingen = i
            break
    if correct_ingen is None:
        correct_ingen = ingen[0]
    return correct_ingen


def compile_ingen(ingen_path: str, args: argparse.Namespace, weak_compilation_flags=False):
    """
    Compiles ingen and returns path to compiled executable.
    If ingen_path is shell script, then it will be returned.
    """
    if os.path.splitext(ingen_path)[1] == '.sh':
        return ingen_path

    compilers = compiler.verify_compilers(args, [ingen_path])
    ingen_exe, compile_log_path = compile.compile_file(ingen_path, package_util.get_executable(ingen_path), compilers,
                                                       weak_compilation_flags)

    if ingen_exe is None:
        compile.print_compile_log(compile_log_path)
        util.exit_with_error('Failed ingen compilation.')
    else:
        print(util.info('Successfully compiled ingen.'))
    return ingen_exe


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


def compile_correct_solution(solution_path: str, args: argparse.Namespace, weak_compilation_flags=False):
    """
    Compiles correct solution and returns path to compiled executable.
    """
    compilers = compiler.verify_compilers(args, [solution_path])
    correct_solution_exe, compile_log_path = compile.compile_file(solution_path, package_util.get_executable(solution_path), compilers,
                                weak_compilation_flags)
    if correct_solution_exe is None:
        util.exit_with_error('Failed compilation of correct solution.',
                                  lambda: compile.print_compile_log(compile_log_path))
    else:
        print(util.info('Successfully compiled correct solution.'))

    return correct_solution_exe


def run_ingen(ingen_exe, working_dir=None):
    """
    Runs ingen and generates all input files.
    :param ingen_exe: path to ingen executable
    :param working_dir: working directory for ingen. If None, then {os.getcwd()}/in is used.
    :return: True if ingen was successful, False otherwise
    """
    if working_dir is None:
        working_dir = os.path.join(os.getcwd(), 'in')

    is_shell = os.path.splitext(ingen_exe)[1] == '.sh'
    if is_shell:
        st = os.stat(ingen_exe)
        os.chmod(ingen_exe, st.st_mode | stat.S_IEXEC)

    process = subprocess.Popen([ingen_exe], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               cwd=working_dir, shell=is_shell)
    while process.poll() is None:
        print(process.stdout.readline().decode('utf-8'), end='')

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
