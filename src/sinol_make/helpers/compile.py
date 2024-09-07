from typing import Tuple, Union
import os
import sys
import shutil
import stat
import subprocess

import sinol_make.helpers.compiler as compiler
from sinol_make import util
from sinol_make.helpers import paths
from sinol_make.helpers.cache import check_compiled, save_compiled, package_util
from sinol_make.interfaces.Errors import CompilationError
from sinol_make.structs.compiler_structs import Compilers


def compile(program, output, compilers: Compilers = None, compile_log=None, compilation_flags='default',
            extra_compilation_args=None, extra_compilation_files=None, clear_cache=False, use_fsanitize=False):
    """
    Compile a program.
    :param program: Path to the program to compile
    :param output: Path to the output file
    :param compilers: Compilers object
    :param compile_log: File to write the compilation log to
    :param compilation_flags: Group of compilation flags to use
    :param extra_compilation_args: Extra compilation arguments
    :param extra_compilation_files: Extra compilation files
    :param clear_cache: Set to True if you want to delete all cached test results.
    :param use_fsanitize: Whether to use fsanitize when compiling C/C++ programs. Sanitizes address and undefined behavior.
    """
    if extra_compilation_args is None:
        extra_compilation_args = []
    if isinstance(extra_compilation_args, str):
        extra_compilation_args = [extra_compilation_args]
    assert isinstance(extra_compilation_args, list) and all(isinstance(arg, str) for arg in extra_compilation_args)

    # Address and undefined sanitizer is not yet supported on Apple Silicon.
    if use_fsanitize and util.is_macos_arm():
        use_fsanitize = False

    if compilation_flags == 'w':
        compilation_flags = 'weak'
    elif compilation_flags == 'o':
        compilation_flags = 'oioioi'
    elif compilation_flags == 'd':
        compilation_flags = 'default'

    if extra_compilation_files is None:
        extra_compilation_files = []

    compiled_exe = check_compiled(program, compilation_flags, use_fsanitize)
    if compiled_exe is not None:
        if compile_log is not None:
            compile_log.write(f'Using cached executable {compiled_exe}\n')
            compile_log.close()
        if os.path.abspath(compiled_exe) != os.path.abspath(output):
            shutil.copy(compiled_exe, output)
        return True

    for file in extra_compilation_files:
        shutil.copy(file, os.path.join(os.path.dirname(output), os.path.basename(file)))

    gcc_compilation_flags = ''
    if compilation_flags == 'weak':
        gcc_compilation_flags = ''  # Disable all warnings
    elif compilation_flags == 'oioioi':
        gcc_compilation_flags = ' -Wall -Wno-unused-result -Werror'  # Same flags as oioioi
    elif compilation_flags == 'default':
        gcc_compilation_flags = ' -Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'
    else:
        util.exit_with_error(f'Unknown compilation flags group: {compilation_flags}')

    if compilers is None:
        compilers = Compilers()

    ext = os.path.splitext(program)[1]
    if ext == '.cpp':
        arguments = [compilers.cpp_compiler_path or compiler.get_cpp_compiler_path(), program] + \
                    extra_compilation_args + ['-o', output] + \
                    f'--std=c++20 -O3 -lm{gcc_compilation_flags} -fdiagnostics-color'.split(' ')
        if use_fsanitize and compilation_flags != 'weak':
            arguments += ['-fsanitize=address,undefined', '-fno-sanitize-recover']
    elif ext == '.c':
        arguments = [compilers.c_compiler_path or compiler.get_c_compiler_path(), program] + \
                    extra_compilation_args + ['-o', output] + \
                    f'--std=gnu99 -O3 -lm{gcc_compilation_flags} -fdiagnostics-color'.split(' ')
        if use_fsanitize and compilation_flags != 'weak':
            arguments += ['-fsanitize=address,undefined', '-fno-sanitize-recover']
    elif ext == '.py':
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            # TODO: Make this work on Windows
            print(util.error('Python is not supported on Windows'))
            pass
        else:
            with open(output, 'w') as output_file, open(program, 'r') as program_file:
                output_file.write('#!/usr/bin/python3\n')
                output_file.write(program_file.read())

            st = os.stat(output)
            os.chmod(output, st.st_mode | stat.S_IEXEC)
        arguments = [compilers.python_interpreter_path, '-m', 'py_compile', program]
    elif ext == '.java':
        raise NotImplementedError('Java compilation is not implemented')
    else:
        raise CompilationError('Unknown file extension: ' + ext)

    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = process.communicate()
    if compile_log is not None:
        compile_log.write(out.decode('utf-8'))
        compile_log.close()
    else:
        print(out.decode('utf-8'))

    if process.returncode != 0:
        raise CompilationError('Compilation failed')
    else:
        save_compiled(program, output, compilation_flags, use_fsanitize, clear_cache)
        return True


def compile_file(file_path: str, name: str, compilers: Compilers, compilation_flags='default',
                 use_fsanitize=False, additional_flags=None, use_extras=True) \
        -> Tuple[Union[str, None], str]:
    """
    Compile a file
    :param file_path: Path to the file to compile
    :param name: Name of the executable
    :param compilers: Compilers object
    :param compilation_flags: Group of compilation flags to use
    :param use_fsanitize: Whether to use fsanitize when compiling C/C++ programs. Sanitizes address and undefined behavior.
    :param additional_flags: Additional flags for c / c++ compiler.
    :param use_extras: Whether to use extra compilation files and arguments from config
    :return: Tuple of (executable path or None if compilation failed, log path)
    """
    config = package_util.get_config()

    extra_compilation_args = []
    extra_compilation_files = []
    if use_extras:
        lang = os.path.splitext(file_path)[1][1:]
        args = config.get("extra_compilation_args", {}).get(lang, [])
        if isinstance(args, str):
            args = [args]
        for arg in args:
            path = os.path.join(os.getcwd(), "prog", arg)
            if os.path.exists(path):
                extra_compilation_args.append(path)
            else:
                extra_compilation_args.append(arg)

        for file in config.get("extra_compilation_files", []):
            extra_compilation_files.append(os.path.join(os.getcwd(), "prog", file))
    if additional_flags is not None:
        extra_compilation_args.append(additional_flags)

    output = paths.get_executables_path(name)
    compile_log_path = paths.get_compilation_log_path(os.path.splitext(name)[0] + '.compile_log')
    with open(compile_log_path, 'w') as compile_log:
        try:
            if compile(file_path, output, compilers, compile_log, compilation_flags, extra_compilation_args,
                       extra_compilation_files, use_fsanitize=use_fsanitize):
                return output, compile_log_path
        except CompilationError:
            pass
        return None, compile_log_path


def print_compile_log(compile_log_path: str):
    """
    Print the first 500 lines of compilation log
    :param compile_log_path: path to the compilation log
    """
    lines_to_print = 500

    with open(compile_log_path, 'r') as compile_log:
        lines = compile_log.readlines()
        for line in lines[:lines_to_print]:
            print(line, end='')
        if len(lines) > lines_to_print:
            print(util.error(f"Compilation log too long. Whole log file at: {compile_log_path}"))
