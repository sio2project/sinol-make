import os
import argparse
from typing import List, Union, Tuple

import yaml

from sinol_make.compilers.compiler import Compiler
from sinol_make.compilers.gcc import GccCompiler
from sinol_make.compilers.gpp import GppCompiler
from sinol_make.compilers.python import PythonCompiler
from sinol_make.helpers import paths
from sinol_make.interfaces.Errors import CompilationError


class CompilerManager:
    available_compilers: List[Compiler] = [GccCompiler(), GppCompiler(), PythonCompiler()]
    def __init__(self, args):
        if args is None:
            self.args = argparse.Namespace(weak_compilation_flags=False)
            self.set_default_compilers()
        else:
            self.args = args
            self.set_compilers()

    @staticmethod
    def get_available_compilers() -> List[Compiler]:
        """
        :return: List of available compilers.
        """
        return CompilerManager.available_compilers

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        """
        Add arguments to the parser.
        """
        for compiler in CompilerManager.get_available_compilers():
            parser.add_argument(compiler.get_argument_flag(), type=str, default=compiler.get_default_compiler(),
                                help=f'{compiler.get_name()} to use (default: {compiler.get_default_compiler()})')

        parser.add_argument('-W', '--weak-compilation-flags', dest='weak_compilation_flags',
                            action='store_true', help='disable all warning flags during C and C++ compilation')

    def set_compilers(self):
        """
        Set compilers based on arguments.
        """
        for compiler in self.get_available_compilers():
            compiler.set_compiler(getattr(self.args, compiler.get_argument_name(), compiler.get_default_compiler()))

    def set_default_compilers(self):
        """
        Set compilers to default.
        """
        for compiler in self.get_available_compilers():
            compiler.set_compiler(compiler.get_default_compiler())

    def get_compiler(self, file_name: str) -> Union[Compiler, None]:
        """
        Get compiler based on file name.
        :param file_name: File name
        :return: Compiler object or None if no compiler is found
        """
        for compiler in self.get_available_compilers():
            if compiler.is_file_supported(file_name):
                return compiler
        return None

    def compile(self, file_path: str, name: str, use_fsanitize: bool = False,
                use_extras: bool = False) -> Tuple[Union[str, None], str]:
        """
        Compile a file.
        :param file_path: Path to file to compile
        :param name: Name of executable.
        :param use_fsanitize: Whether to use fsanitize when compiling C/C++ programs. Sanitizes address and undefined behavior.
        :param use_extras: Whether to use extra compilation files and arguments specified in config.yml
        :return: Tuple of (path to executable, path to compilation log)
        """
        os.makedirs(paths.get_executables_path(), exist_ok=True)
        os.makedirs(paths.get_compilation_log_path(), exist_ok=True)

        output = paths.get_executables_path(name)
        compiler = self.get_compiler(file_path)
        if compiler is None:
            raise CompilationError(f'No compiler found for file {file_path}')

        if use_extras:
            with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
                config = yaml.load(config_file, Loader=yaml.FullLoader)

            extra_compilation_files = [os.path.join(os.getcwd(), "prog", file)
                                       for file in config.get("extra_compilation_files", [])]
            lang = os.path.splitext(file_path)[1][1:]
            args = config.get('extra_compilation_args', {}).get(lang, [])
            if isinstance(args, str):
                args = [args]
            extra_compilation_args = []
            for arg in args:
                if os.path.exists(os.path.join(os.getcwd(), "prog", arg)):
                    extra_compilation_args.append(os.path.join(os.getcwd(), "prog", arg))
                else:
                    extra_compilation_args.append(arg)
        else:
            extra_compilation_files = None
            extra_compilation_args = None

        compile_log_path = paths.get_compilation_log_path(os.path.basename(file_path) + '.compile_log')
        with open(compile_log_path, 'w') as compile_log:
            try:
                if compiler.compile(file_path, output, compile_log, self.args.weak_compilation_flags,
                                    extra_compilation_args, extra_compilation_files, use_fsanitize):
                    return output, compile_log_path
            except CompilationError:
                pass
            return None, compile_log_path

    @staticmethod
    def print_compile_log(compile_log_path: str):
        """
        Print the first 500 lines of compilation log
        :param compile_log_path: path to the compilation log
        """

        with open(compile_log_path, 'r') as compile_log:
            lines = compile_log.readlines()
            for line in lines[:500]:
                print(line, end='')
