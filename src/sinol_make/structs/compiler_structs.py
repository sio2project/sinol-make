from dataclasses import dataclass

from sinol_make.helpers import compiler


@dataclass
class Compilers:
    c_compiler_path: str
    cpp_compiler_path: str
    python_interpreter_path: str
    java_compiler_path: str

    def __init__(self, c_compiler_path: str = None, cpp_compiler_path: str = None, python_interpreter_path: str = None, java_compiler_path: str = None):
        self.c_compiler_path = c_compiler_path or compiler.get_c_compiler_path()
        self.cpp_compiler_path = cpp_compiler_path or compiler.get_cpp_compiler_path()
        self.python_interpreter_path = python_interpreter_path or compiler.get_python_interpreter_path()
        self.java_compiler_path = java_compiler_path or compiler.get_java_compiler_path()
