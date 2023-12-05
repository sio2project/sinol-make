import re
import subprocess
from typing import Tuple, List, Union

from sinol_make.compilers.CompilersManager import CompilerManager
from sinol_make.executor import Executor
from sinol_make.helpers import cache
from sinol_make.interfaces.Errors import CheckerOutputException
from sinol_make.programs.program import Program
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest


class Checker(Program):

    def __init__(self, executor: Executor, compiler_manager: CompilerManager, task_id: str,
                 file_path: Union[str, None] = None, executable_name: Union[str, None] = None):
        super().__init__(executor, compiler_manager, task_id, file_path, executable_name)
        self._answer_test = None
        self._output_file_path = None
        self._input_test = None

    def get_name(self) -> str:
        return "checker"

    def _regex_match(self) -> re.Pattern:
        return re.compile(r'%schk\.(cpp|cc|java|py|pas)' % self.task_id)

    def get_dir(self) -> str:
        return "prog"

    def compile(self) -> Tuple[Union[str, None], str]:
        if cache.has_file_changed(self.file_path):
            cache.remove_results_cache()
        return super().compile()

    def check_output(self, input_test: InputTest, output_file_path: str,
                     answer_test: OutputTest, cwd = None) -> Tuple[bool, int]:
        """
        Checks if the output is correct.
        :param input_test: Input test
        :param output_file_path: Path to the output file created by running a solution
        :param answer_test: Output test
        :param cwd: Current working directory. If None, the current working directory is used.
        :return: Returns a tuple of (is_correct, percent of points assigned).
        """
        exit_code, stdout, _ = self.run(input_test, output_file_path, answer_test, cwd)
        output = stdout.decode('utf-8').splitlines()

        if len(output) == 0:
            raise CheckerOutputException("Checker output is empty")

        if output[0].strip() == "OK":
            points = 100
            if len(output) >= 3:
                try:
                    points = int(output[2].strip())
                except ValueError:
                    pass

            return True, points
        else:
            return False, 0


    def _run_arguments(self) -> List[str]:
        if self._input_test is None or self._output_file_path is None or self._answer_test is None:
            raise ValueError("Checker not initialized")
        return [self.executable_path, self._input_test.file_path, self._output_file_path, self._answer_test.file_path]

    def run(self, input_test: InputTest, output_file_path: str,
            answer_test: OutputTest, cwd = None) -> Tuple[int, bytes, bytes]:
        """
        Run checker for a specified test.
        :param input_test: Input test
        :param output_file_path: Path to the output file created by running a solution
        :param answer_test: Output test
        :param cwd: Current working directory. If None, the current working directory is used.
        :return: Tuple of exit code, stdout and stderr.
        """
        self._input_test = input_test
        self._output_file_path = output_file_path
        self._answer_test = answer_test
        return super().run(stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=cwd, return_out=True)
