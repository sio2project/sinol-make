import sys

import argparse

from sinol_make.helpers import compiler


def add_compilation_arguments(parser: argparse.ArgumentParser):
    if sys.platform == 'darwin':
        gcc_versions = 'gcc-9, gcc-10, gcc-11'
        gpp_versions = 'g++-9, g++-10, g++-11'
    else:
        gcc_versions = 'gcc'
        gpp_versions = 'g++'

    parser.add_argument('--c_compiler_path', type=str, default=compiler.get_c_compiler_path(),
                        help=f'C compiler to use (default {gcc_versions})')
    parser.add_argument('--cpp_compiler_path', type=str, default=compiler.get_cpp_compiler_path(),
                        help=f'C++ compiler to use (default {gpp_versions})')
    parser.add_argument('--python_interpreter_path', type=str, default=compiler.get_python_interpreter_path(),
                        help='Python interpreter to use (default: python3)')
    parser.add_argument('--java_compiler_path', type=str, default=compiler.get_java_compiler_path(),
                        help='Java compiler to use (default: javac)')
