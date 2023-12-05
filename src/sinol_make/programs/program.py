import os
import re
from typing import Union, List, Tuple

from sinol_make.executor import Executor
from sinol_make.helpers import paths, cache
from sinol_make.structs.cache_structs import CacheFile
from sinol_make.structs.timetool_structs import TimeToolResult


class Program:
    def __init__(self, executor: Executor, compiler_manager: "CompilerManager", task_id: str,
                 file_path: Union[str, None] = None, executable_name: Union[str, None] = None):
        """
        :param executor: Executor.
        :param compiler_manager: Compiler manager.
        :param task_id: Task ID.
        :param file_path: File path to the program. If None, will search for the program in the proper directory.
        :param executable_name: Name of the executable. If None, will be the same as the file name with .e extension.
        """
        self.task_id = task_id
        self.file_path = self.find(file_path)
        if executable_name is None:
            executable_name = os.path.basename(self.file_path) + '.e'
        self.executable_path = paths.get_executables_path(os.path.basename(executable_name))
        self.executor = executor
        self.compiler_manager = compiler_manager
        self.basename = os.path.basename(self.file_path)
        self.lang = self.get_lang()

    def __str__(self):
        return f"<{self.get_name()} {self.get_dir()}/{self.basename}>"

    def __repr__(self):
        return str(self)

    def get_name(self) -> str:
        """
        :return: Name of the program.
        """
        raise NotImplementedError()

    def get_lang(self) -> str:
        """
        :return: Language of the program.
        """
        return os.path.splitext(self.basename)[1][1:].lower()

    def get_dir(self) -> str:
        """
        :return: Directory of the program.
        """
        raise NotImplementedError()

    def get_cache_file(self) -> CacheFile:
        """
        :return: Cache file for this program.
        """
        return cache.get_cache_file(self.file_path)

    def _regex_match(self) -> re.Pattern:
        """
        :return: Regex pattern for matching a program. Should match all possible programs of this type.
        """
        raise NotImplementedError()

    def _regex_matches(self) -> List[re.Pattern]:
        """
        :return: Regex patterns for matching a program. Should be in descending order of priority.
        """
        return []

    def _is_match(self, file_path: str) -> bool:
        """
        :param file_path: File path to check.
        :return: True if the file path matches the regex pattern.
        """
        return self._regex_match().match(file_path) is not None

    def find(self, file_path: Union[str, None]):
        """
        Find the program. If file_path is not None, will check if the file path matches the regex pattern and exists.
        :param file_path: File path to check.
        :return: Real path to the program.
        """
        if file_path is None:
            matches = self._regex_matches()
            if len(matches) == 0:
                matches = [self._regex_match()]

            for match in matches:
                files = list(filter(lambda f: match.match(os.path.basename(f)) is not None, os.listdir(self.get_dir())))
                if len(files) > 0:
                    return os.path.realpath(os.path.join(self.get_dir(), files[0]))
            raise FileNotFoundError(f'No {self.get_name()} program found.')
        else:
            basename = os.path.basename(file_path)
            if self._is_match(basename):
                if os.path.exists(file_path):
                    return os.path.realpath(file_path)
                elif os.path.exists(os.path.join(self.get_dir(), file_path)):
                    return os.path.realpath(os.path.join(self.get_dir(), file_path))
            raise FileNotFoundError(f'File {file_path} does not exist or is not a {self.get_name()} program.')

    def _use_fsanitize(self) -> bool:
        """
        :return: True if the program should be compiled with fsanitize.
        """
        return False

    def _use_extras(self) -> bool:
        """
        :return: True if the program should be compiled with extra compilation files and arguments.
        """
        return False

    def compile(self) -> Tuple[Union[str, None], str]:
        """
        Compile the program.
        """
        return self.compiler_manager.compile(self.file_path, self.executable_path, use_fsanitize=self._use_fsanitize(),
                                             use_extras=self._use_extras())

    def _run_arguments(self) -> List[str]:
        """
        :return: Arguments for running the program.
        """
        return [self.executable_path]

    def run(self, stdin = None, stdout = None, stderr = None,
            cwd = None, return_out = False, shell = False) -> Union[int, Tuple[int, bytes, bytes]]:
        """
        Run the program.
        :param stdin: stdin of the program.
        :param stdout: stdout of the program.
        :param stderr: stderr of the program.
        :param cwd: Current working directory. If None, the current working directory is used.
        :param return_out: If True, returns stdout and stderr of the program (if they were `subprocess.PIPE`).
        :param shell: If True, runs the program in a shell.
        :return: Return code of the program.
        """
        return self.executor.run(self._run_arguments(), stdin=stdin, stdout=stdout, stderr=stderr,
                                 cwd=cwd, return_out=return_out, shell=shell)

    def run_timetool(self, result_file_path: str, stdin = None, stdout = None, stderr = None, time_limit = None,
                     memory_limit = None, cwd = None) -> TimeToolResult:
        """
        Run the program with the timetool.
        :param result_file_path: Path to file where the time tool's results are saved.
        :param stdin: Stdin.
        :param stdout: Stdout.
        :param stderr: Stderr.
        :param time_limit: Time limit.
        :param memory_limit: Memory limit.
        :param cwd: Current working directory. If None, the current working directory is used.
        :return: Result of the timetool run.
        """
        return self.executor.run_timetool(self._run_arguments(), result_file_path, stdin, stdout, stderr,
                                          time_limit, memory_limit, cwd)
