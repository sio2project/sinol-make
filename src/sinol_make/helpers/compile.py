from typing import Tuple, Union
import os
import sys
import shutil
import stat
import subprocess
import yaml

import sinol_make.helpers.compiler as compiler
from sinol_make.interfaces.Errors import CompilationError
from sinol_make.structs.compiler_structs import Compilers


def compile(program, output, compilers: Compilers = None, compile_log = None, weak_compilation_flags = False,
            extra_compilation_args = None, extra_compilation_files = None):
    """
    Compile a program.
    :param program: Path to the program to compile
    :param output: Path to the output file
    :param compilers: Compilers object
    :param compile_log: File to write the compilation log to
    :param weak_compilation_flags: If True, disable all warnings
    :param extra_compilation_args: Extra compilation arguments
    :param extra_compilation_files: Extra compilation files
    """
    if extra_compilation_args is None:
        extra_compilation_args = []
    if extra_compilation_files is None:
        extra_compilation_files = []

    for file in extra_compilation_files:
        shutil.copy(file, os.path.join(os.path.dirname(output), os.path.basename(file)))

    gcc_compilation_flags = '-Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'
    if weak_compilation_flags:
        gcc_compilation_flags = '-w'  # Disable all warnings

    if compilers is None:
        compilers = Compilers()

    ext = os.path.splitext(program)[1]
    arguments = []
    if ext == '.cpp':
        arguments = [compilers.cpp_compiler_path or compiler.get_cpp_compiler_path(), program] + \
                    extra_compilation_args + ['-o', output] + \
                    f'--std=c++17 -O3 -lm {gcc_compilation_flags} -fdiagnostics-color'.split(' ')
    elif ext == '.c':
        arguments = [compilers.c_compiler_path or compiler.get_c_compiler_path(), program] + \
                    extra_compilation_args + ['-o', output] + \
                    f'--std=c17 -O3 -lm {gcc_compilation_flags} -fdiagnostics-color'.split(' ')
    elif ext == '.py':
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            # TODO: Make this work on Windows
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
    process.wait()
    out, _ = process.communicate()
    if compile_log is not None:
        compile_log.write(out.decode('utf-8'))
        compile_log.close()
    else:
        print(out.decode('utf-8'))

    if process.returncode != 0:
        raise CompilationError('Compilation failed')
    else:
        return True


def compile_file(file_path: str, name: str, compilers: Compilers, weak_compilation_flags = False) \
        -> Tuple[Union[str, None], str]:
    """
    Compile a file
    :param file_path: Path to the file to compile
    :param name: Name of the executable
    :param compilers: Compilers object
    :param weak_compilation_flags: Use weaker compilation flags
    :return: Tuple of (executable path or None if compilation failed, log path)
    """

    executable_dir = os.path.join(os.getcwd(), 'cache', 'executables')
    compile_log_dir = os.path.join(os.getcwd(), 'cache', 'compilation')
    os.makedirs(executable_dir, exist_ok=True)
    os.makedirs(compile_log_dir, exist_ok=True)

    with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    extra_compilation_files = [os.path.join(os.getcwd(), "prog", file)
                               for file in config.get("extra_compilation_files", [])]
    extra_compilation_args = [os.path.join(os.getcwd(), "prog", file)
                              for file in config.get('extra_compilation_args', {}).get(os.path.splitext(file_path)[1][1:], [])]

    output = os.path.join(executable_dir, name)
    compile_log_path = os.path.join(compile_log_dir, os.path.splitext(name)[0] + '.compile_log')
    with open(compile_log_path, 'w') as compile_log:
        try:
            if compile(file_path, output, compilers, compile_log, weak_compilation_flags, extra_compilation_args,
                       extra_compilation_files):
                return output, compile_log_path
        except CompilationError:
            pass
        return None, compile_log_path


def print_compile_log(compile_log_path: str):
    """
    Print the first 500 lines of compilation log
    :param compile_log_path: path to the compilation log
    """

    with open(compile_log_path, 'r') as compile_log:
        lines = compile_log.readlines()
        for line in lines[:500]:
            print(line, end='')
