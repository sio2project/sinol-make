from typing import List

from sinol_make import util
from sinol_make.compilers.compiler import Compiler


class GppCompiler(Compiler):
    def get_name(self) -> str:
        return 'C++ compiler'

    def get_argument_flag(self) -> str:
        return '--cpp-compiler-path'

    def get_possible_compilers(self) -> List[str]:
        if util.is_macos():
            return ['g++-12', 'g++-11', 'g++-10', 'g++-9']
        else:
            return ['g++']

    def get_compiler_path(self) -> str:
        return self.compiler_name

    def _supported_extensions(self) -> List[str]:
        return ['.cpp']

    def _compilation_args(self, file_path: str, output: str, weak_compilation_flags: bool,
                            extra_compilation_args: List[str], extra_compilation_files: List[str],
                            use_fsanitize: bool) -> List[str]:
        args = [self.get_compiler_path(), file_path] + extra_compilation_args + ['-o', output] + \
             ['--std=c++20', '-O3', '-lm', '-fdiagnostics-color']
        if weak_compilation_flags:
            args += ['-w']
        else:
            args += ['-Werror', '-Wall', '-Wextra', '-Wshadow', '-Wconversion', '-Wno-unused-result', '-Wfloat-equal']
        if use_fsanitize:
            args += ['-fsanitize=address,undefined', '-fno-sanitize-recover']
        return args
