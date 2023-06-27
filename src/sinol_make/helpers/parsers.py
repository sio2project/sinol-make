import argparse

from sinol_make.helpers import compiler


def add_compilation_arguments(parser: argparse.ArgumentParser):
	parser.add_argument('--c_compiler_path', type=str, default=compiler.get_c_compiler_path(),
						help='C compiler to use (default for Linux and Windows: gcc, default for Mac: gcc-9 or gcc-10)')
	parser.add_argument('--cpp_compiler_path', type=str, default=compiler.get_cpp_compiler_path(),
						help='C++ compiler to use (default for Linux and Windows: g++, default for Mac: g++-9 or g++-10)')
	parser.add_argument('--python_interpreter_path', type=str, default=compiler.get_python_interpreter_path(),
						help='Python interpreter to use (default: python3)')
	parser.add_argument('--java_compiler_path', type=str, default=compiler.get_java_compiler_path(),
						help='Java compiler to use (default: javac)')
