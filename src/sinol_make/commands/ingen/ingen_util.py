import stat
import subprocess

import argparse
import os

from sinol_make import util
from sinol_make.helpers import package_util, compiler, compile


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


def compile_ingen(ingen_path: str, args: argparse.Namespace, compilation_flags='default', use_fsanitize=False):
    """
    Compiles ingen and returns path to compiled executable.
    If ingen_path is shell script, then it will be returned.
    """
    if os.path.splitext(ingen_path)[1] == '.sh':
        return ingen_path

    compilers = compiler.verify_compilers(args, [ingen_path])
    ingen_exe, compile_log_path = compile.compile_file(ingen_path, package_util.get_executable(ingen_path),
                                                       compilers, compilation_flags, use_fsanitize=use_fsanitize,
                                                       additional_flags='-D_INGEN', use_extras=False)

    if ingen_exe is None:
        compile.print_compile_log(compile_log_path)
        util.exit_with_error('Failed ingen compilation.')
    else:
        print(util.info('Successfully compiled ingen.'))
    return ingen_exe


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

    print(util.bold(' Ingen output '.center(util.get_terminal_size()[1], '=')))
    process = subprocess.Popen([ingen_exe], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               cwd=working_dir, shell=is_shell)
    whole_output = ''
    while process.poll() is None:
        out = process.stdout.readline().decode('utf-8')
        if out != '':
            print(out, end='')
            whole_output += out
    out = process.stdout.read().decode('utf-8')
    whole_output += out
    print(out, end='')
    exit_code = process.returncode
    print(util.bold(' End of ingen output '.center(util.get_terminal_size()[1], '=')))

    if util.has_sanitizer_error(whole_output, exit_code):
        print(util.warning('Warning: if ingen failed due to sanitizer errors, you can either run '
                           '`sudo sysctl vm.mmap_rnd_bits=28` to fix this or disable sanitizers with the '
                           '--no-fsanitize flag.'))

    return exit_code == 0
