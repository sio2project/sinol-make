from typing import Tuple

import sinol_make.helpers.compiler as compiler
from sinol_make.interfaces.Errors import CompilationError
from sinol_make.structs.compiler_structs import Compilers
import os, subprocess, sys

def compile(program, output, compilers: Compilers = None, compile_log = None, weak_compilation_flags = False):
    """
    Compile a program
    compilers - A Compilers object with compilers to use. If None, default compilers will be used.
    """
    gcc_compilation_flags = '-Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'
    if weak_compilation_flags:
        gcc_compilation_flags = '-w' # Disable all warnings

    if compilers is None:
        compilers = Compilers()

    ext = os.path.splitext(program)[1]
    arguments = []
    if ext == '.cpp':
        arguments = [compilers.cpp_compiler_path or compiler.get_cpp_compiler_path(), program, '-o', output] + \
                    f'--std=c++17 -O3 -lm {gcc_compilation_flags} -fdiagnostics-color'.split(' ')
    elif ext == '.c':
        arguments = [compilers.c_compiler_path, program, '-o', output] + \
                    f'--std=c17 -O3 -lm {gcc_compilation_flags} -fdiagnostics-color'.split(' ')
    elif ext == '.py':
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            # TODO: Make this work on Windows
            pass
        else:
            open(output, 'w').write('#!/usr/bin/python3\n')
            open(output, 'a').write(open(program, 'r').read())
            subprocess.call(['chmod', '+x', output])
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


def compile_file(file_path: str, name: str, compilers: Compilers, weak_compilation_flags = False) -> Tuple[str or None, str]:
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

    output = os.path.join(executable_dir, name)
    compile_log_path = os.path.join(compile_log_dir, os.path.splitext(name)[0] + '.compile_log')
    compile_log = open(compile_log_path, 'w')

    try:
        if compile(file_path, output, compilers, compile_log, weak_compilation_flags):
            return output, compile_log_path
        else:
            return None, compile_log_path
    except CompilationError:
        return None, compile_log_path


def print_compile_log(compile_log_path: str):
    """
    Print the first 500 lines of compilation log
    :param compile_log_path: path to the compilation log
    """

    compile_log = open(compile_log_path, 'r')
    lines = compile_log.readlines()
    compile_log.close()
    for line in lines[:500]:
        print(line, end='')
