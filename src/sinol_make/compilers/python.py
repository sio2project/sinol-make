from typing import List
import os
import stat

from sinol_make.compilers.compiler import Compiler


class PythonCompiler(Compiler):
    def get_name(self) -> str:
        return 'Python interpreter'

    def get_argument_flag(self) -> str:
        return '--python-interpreter-path'

    def get_possible_compilers(self) -> List[str]:
        return ['python3.11', 'python3.12', 'python3.10', 'python3.9', 'python3.8', 'python3.7', 'python3', 'python']

    def get_compiler_path(self) -> str:
        return self.compiler_name

    def _supported_extensions(self) -> List[str]:
        return ['.py']

    def _use_custom_compilation(self) -> bool:
        return True

    def _custom_compilation(self, file_path: str, output: str, weak_compilation_flags: bool,
                            extra_compilation_args: List[str], extra_compilation_files: List[str],
                            use_fsanitize: bool) -> List[str]:
        with open(output, 'w') as output_file, open(file_path, 'r') as program_file:
            output_file.write(f'#!/usr/bin/{self.get_compiler_path()}\n')
            output_file.write(program_file.read())

        st = os.stat(output)
        os.chmod(output, st.st_mode | stat.S_IEXEC)
        return True
