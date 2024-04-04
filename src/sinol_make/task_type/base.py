from typing import List, Dict, Any, Tuple

from sinol_make import util
from sinol_make.interfaces.Errors import CheckerOutputException


class BaseTaskType:
    def __init__(self, task_id):
        self.task_id = task_id
        self._has_checker = False

    def get_files_to_compile(self) -> List[Tuple[str, List[str], Dict[str, Any]]]:
        """
        Returns a list of tuples where:
         - the first element is what will be printed in `Compiling {first_element}`
         - the second element is a list of *args passed to `run.compile`
         - the third element is a dictionary of **kwargs passed to `run.compile`
        """
        pass

    def has_checker(self) -> bool:
        return self._has_checker

    def _run_checker(self, input_file, output_file_path, answer_file_path) -> List[str]:
        return []

    def _parse_checker_output(self, checker_output: List[str]) -> Tuple[bool, int]:
        """
        Parse the output of the checker
        :return: tuple of (is_correct, score)
        """
        if len(checker_output) == 0:
            raise CheckerOutputException("Checker output is empty.")

        if checker_output[0].strip() == "OK":
            points = 100
            if len(checker_output) >= 3:
                try:
                    points = int(checker_output[2].strip())
                except ValueError:
                    pass

            return True, points
        else:
            return False, 0

    def check_output(self, input_file, output_file_path, output, answer_file_path) -> Tuple[bool, int]:
        if self._has_checker:
            with open(output_file_path, "w") as output_file:
                output_file.write("\n".join(output) + "\n")
            checker_output = self._run_checker(input_file, output_file_path, answer_file_path)
            return self._parse_checker_output(checker_output)
        else:
            with open(answer_file_path, "r") as answer_file:
                correct = util.lines_diff(output, answer_file.readlines())
            return correct, 100 if correct else 0
