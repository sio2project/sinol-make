from typing import List, Union
import os
import subprocess
import shutil

from sinol_make import util
from sinol_make.helpers import cache
from sinol_make.helpers.cache import save_compiled
from sinol_make.interfaces.Errors import CompilationError


class Compiler:
    def __init__(self):
        self.compiler_name = ""

    def get_name(self) -> str:
        """
        :return: Compiler name (for example `C++ compiler`). Used for displaying help.
        """
        raise NotImplementedError()

    def get_argument_flag(self) -> str:
        """
        :return: Compiler argument name (for example `--cpp-compiler-path`). Used for displaying help.
        """
        raise NotImplementedError()

    def get_argument_name(self) -> str:
        """
        :return: Compiler argument name (for example `cpp_compiler_path`). Used for displaying help.
        """
        return self.get_argument_flag()[2:].replace('-', '_')

    def get_possible_compilers(self) -> List[str]:
        """
        :return: List of possible compilers. They should be in descending order of importance.
        """
        raise NotImplementedError()

    def get_available_compilers(self) -> list:
        """
        :return: List of names of available compilers. Used for displaying help.
        """
        res = []
        for compiler in self.get_possible_compilers():
            if self._check_if_installed(compiler):
                res.append(compiler)
        return res

    def get_default_compiler(self) -> str:
        """
        :return: Default compiler. Used when no compiler is passed as an argument and for displaying help message.
        """
        for compiler in self.get_possible_compilers():
            if self._check_if_installed(compiler):
                return compiler
        return None

    def set_compiler(self, compiler_name: str):
        """
        Set compiler. Called when compiler is passed as an argument.
        """
        if compiler_name not in self.get_available_compilers():
            raise ValueError('Compiler not available')
        self.compiler_name = compiler_name

    def get_compiler_path(self) -> str:
        """
        :return: Path to compiler. `self.compiler_name` is set.
        """
        raise NotImplementedError()

    def _supported_extensions(self) -> List[str]:
        """
        :return: List of supported extensions
        """
        raise NotImplementedError()

    def is_file_supported(self, file_path: str) -> bool:
        """
        Check if file supported by this compiler
        :param file_path: Path to file
        :return: True if file supported by this compiler
        """
        return any(file_path.endswith(ext) for ext in self._supported_extensions())

    def _compilation_args(self, file_path: str, output: str, weak_compilation_flags: bool,
                          extra_compilation_args: List[str], extra_compilation_files: List[str],
                          use_fsanitize: bool) -> List[str]:
        """
        :param file_path: Path to file
        :param output: Path to output file
        :param weak_compilation_flags: If True, disable all warnings
        :param extra_compilation_args: Extra compilation arguments
        :return: List of arguments for compilation
        """
        raise NotImplementedError()

    def _use_custom_compilation(self) -> bool:
        """
        :return: True if custom compilation is used
        """
        return False

    def _custom_compilation(self, file_path: str, output: str, weak_compilation_flags: bool,
                            extra_compilation_args: List[str], extra_compilation_files: List[str],
                            use_fsanitize: bool) -> bool:
        """
        Custom compilation. Called when `_use_custom_compilation` returns True.
        """
        raise NotImplementedError()

    def compile(self, file_path: str, output: str, compile_log = None, weak_compilation_flags: bool = False,
                extra_compilation_args: Union[List[str], str] = None, extra_compilation_files: List[str] = None,
                use_fsanitize: bool = False):
        """
        Compile a file.
        :param file_path: Path to file
        :param output: Path to output file
        :param compile_log: File to write the compilation log to
        :param weak_compilation_flags: If True, disable all warnings
        :param extra_compilation_args: Extra compilation arguments
        :param extra_compilation_files: Extra compilation files
        :param use_fsanitize: Whether to use fsanitize when compiling C/C++ programs. Sanitizes address and undefined behavior.
        """
        if extra_compilation_args is None:
            extra_compilation_args = []
        if isinstance(extra_compilation_args, str):
            extra_compilation_args = [extra_compilation_args]
        if extra_compilation_files is None:
            extra_compilation_files = []

        # Address and undefined sanitizer is not yet supported on Apple Silicon.
        if use_fsanitize and util.is_macos_arm():
            use_fsanitize = False

        compiled_exe = cache.check_compiled(file_path)
        if compiled_exe is not None:
            if compile_log is not None:
                compile_log.write(f'Using cached executable {compiled_exe}\n')
                compile_log.close()
            if os.path.abspath(compiled_exe) != os.path.abspath(output):
                shutil.copy(compiled_exe, output)
            return True

        for file in extra_compilation_files:
            shutil.copy(file, os.path.join(os.path.dirname(output), os.path.basename(file)))

        if not self._use_custom_compilation():
            arguments = self._compilation_args(file_path, output, weak_compilation_flags, extra_compilation_args,
                                               extra_compilation_files, use_fsanitize)
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.wait()
            out, _ = process.communicate()
            if compile_log is not None:
                compile_log.write(out.decode('utf-8'))
                compile_log.close()
            else:
                print(out.decode('utf-8'))

            if process.returncode != 0:
                raise CompilationError(f'Compilation failed with exit code {process.returncode}')
            else:
                save_compiled(file_path, output)
                return True
        else:
            if self._custom_compilation(file_path, output, weak_compilation_flags, extra_compilation_args,
                                        extra_compilation_files, use_fsanitize):
                save_compiled(file_path, output)
                return True
            else:
                raise CompilationError('Compilation failed')

    def _check_if_installed(self, compiler: str):
        """
        Check if a compiler is installed.
        :param compiler: Compiler to check.
        :return: True if compiler is installed.
        """

        try:
            subprocess.call([compiler, '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            return False
        return True
