import sinol_make.helpers.compiler as compiler
from sinol_make.interfaces.Errors import CompilationError
import os, subprocess, sys

def compile(program, output, compilers = None, compile_log = None, weak_compilation_flags = False):
    """
    Compile a program
    compilers - A dictionary of compilers to use. If not set, the default compilers will be used
    """
    gcc_compilation_flags = '-Werror -Wall -Wextra -Wshadow -Wconversion -Wno-unused-result -Wfloat-equal'
    if weak_compilation_flags:
        gcc_compilation_flags = '-w' # Disable all warnings

    ext = os.path.splitext(program)[1]
    arguments = []
    if ext == '.cpp':
        arguments = [compilers['cpp_compiler_path'] or compiler.get_cpp_compiler_path(), program, '-o', output] + \
                    f'--std=c++17 -O3 -lm {gcc_compilation_flags} -fdiagnostics-color'.split(' ')
    elif ext == '.c':
        arguments = [compilers['c_compiler_path'] or compiler.get_c_compiler_path(), program, '-o', output] + \
                    f'--std=c17 -O3 -lm {gcc_compilation_flags} -fdiagnostics-color'.split(' ')
    elif ext == '.py':
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            # TODO: Make this work on Windows
            pass
        else:
            open(output, 'w').write('#!/usr/bin/python3\n')
            open(output, 'a').write(open(program, 'r').read())
            subprocess.call(['chmod', '+x', output])
        arguments = [compilers['python_interpreter_path'] or compiler.get_python_interpreter_path(), '-m', 'py_compile', program]
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
