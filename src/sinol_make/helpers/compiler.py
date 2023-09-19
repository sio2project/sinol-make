from typing import List

import argparse
import os

import sinol_make.util as util
import sys, subprocess

from sinol_make.structs.compiler_structs import Compilers


def check_if_installed(compiler):
    """
    Check if a compiler is installed
    """

    try:
        subprocess.call([compiler, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return False

    return True


def get_c_compiler_path():
    """
    Get the C compiler
    """

    if sys.platform == 'win32' or sys.platform == 'cygwin' or sys.platform == 'linux':
        if not check_if_installed('gcc'):
            return None
        else:
            return 'gcc'
    elif sys.platform == 'darwin':
        for i in [9, 10, 11]:
            compiler = 'gcc-' + str(i)
            if check_if_installed(compiler):
                return compiler

        return None


def get_cpp_compiler_path():
    """
    Get the C++ compiler
    """

    if sys.platform == 'win32' or sys.platform == 'cygwin' or sys.platform == 'linux':
        if not check_if_installed('g++'):
            return None
        else:
            return 'g++'
    elif sys.platform == 'darwin':
        if check_if_installed('g++-12'):  # g++12 is currently the default compiler on sio.
            return 'g++-12'
        for i in [9, 10, 11]:
            compiler = 'g++-' + str(i)
            if check_if_installed(compiler):
                return compiler

        return None


def get_python_interpreter_path():
    """
    Get the Python interpreter
    """

    if check_if_installed('python3.11'):  # python3.11 is currently the default interpreter on sio.
        return 'python3.11'
    for ver in ['3.9', '3.8', '3.7', '3']:
        if check_if_installed('python' + ver):
            return 'python' + ver
    return None


def get_java_compiler_path():
    """
    Get the Java compiler
    """

    if not check_if_installed('javac'):
        return None
    else:
        return 'javac'


def get_default_compilers():
    """
    Get the default compilers
    """
    return argparse.Namespace(
        c_compiler_path=get_c_compiler_path(),
        cpp_compiler_path=get_cpp_compiler_path(),
        python_interpreter_path=get_python_interpreter_path(),
        java_compiler_path=get_java_compiler_path()
    )


def verify_compilers(args: argparse.Namespace, solutions: List[str]) -> Compilers:
    """
    Verify that specified compilers exist.
    :param args: argparse.Namespace arguments
    :param solutions: List of solutions (used for checking if a compiler is specified)
    :return: Compilers object with all the compilers
    """
    for solution in solutions:
        ext = os.path.splitext(solution)[1]
        compiler = ""
        tried = ""
        flag = ""
        if ext == '.c' and args.c_compiler_path is None:
            compiler = 'C compiler'
            flag = '--c-compiler-path'
            if sys.platform == 'darwin':
                tried = 'gcc-{9,10}'
            else:
                tried = 'gcc'
        elif ext == '.cpp' and args.cpp_compiler_path is None:
            compiler = 'C++ compiler'
            flag = '--cpp-compiler-path'
            if sys.platform == 'darwin':
                tried = 'g++-{9,10}'
            else:
                tried = 'g++'
        elif ext == '.py' and args.python_interpreter_path is None:
            compiler = 'Python interpreter'
            flag = '--python-interpreter-path'
            tried = 'python3'
        elif ext == '.java' and args.java_compiler_path is None:
            compiler = 'Java compiler'
            flag = '--java-compiler-path'
            tried = 'javac'

        if compiler != "":
            util.exit_with_error(
                'Couldn\'t find a %s. Tried %s. Try specifying a compiler with %s.' % (compiler, tried, flag))

    return Compilers(
        c_compiler_path=args.c_compiler_path,
        cpp_compiler_path=args.cpp_compiler_path,
        python_interpreter_path=args.python_interpreter_path,
        java_compiler_path=args.java_compiler_path
    )
