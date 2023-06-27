from dataclasses import dataclass


@dataclass
class Compilers:
    c_compiler_path: str
    cpp_compiler_path: str
    python_interpreter_path: str
    java_compiler_path: str
