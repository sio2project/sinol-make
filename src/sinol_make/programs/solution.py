import os
import re
from typing import List

from sinol_make.programs.program import Program


class Solution(Program):
    def get_name(self) -> str:
        return "solution"

    def _regex_matches(self) -> List[re.Pattern]:
        return [
            re.compile(r"^%s\.(cpp|cc|java|py|pas)$" % self.task_id),
            re.compile(r"^%s[bs]?[0-9]*(_.*)?\.(cpp|cc|java|py|pas)$" % self.task_id),
        ]

    @staticmethod
    def static_regex_matches(task_id: str) -> List[re.Pattern]:
        return [
            re.compile(r"^%s\.(cpp|cc|java|py|pas)$" % task_id),
            re.compile(r"^%s[bs]?[0-9]*(_.*)?\.(cpp|cc|java|py|pas)$" % task_id),
        ]

    def _regex_match(self) -> re.Pattern:
        return re.compile(r"^%s[bs]?[0-9]*(_.*)?\.(cpp|cc|java|py|pas)$" % self.task_id)

    @staticmethod
    def get_correct_solution_file(task_id: str) -> str:
        match = Solution.static_regex_matches(task_id)[0]
        for file in os.listdir("prog"):
            if match.match(file) is not None:
                return os.path.abspath(os.path.join("prog", file))
        raise FileNotFoundError(f"Correct solution for task {task_id} does not exist.")

    def get_dir(self) -> str:
        return "prog"

    def _use_extras(self) -> bool:
        return True

    def is_correct_solution(self) -> bool:
        """
        :return: True if the solution is the main correct solution.
        """
        regex = self._regex_matches()[0]
        return regex.match(self.basename) is not None

    def is_bad(self) -> bool:
        """
        :return: True if the solution is a bad solution (`b` after task id in name).
        """
        return self.basename[len(self.task_id)] == 'b'

    def is_slow(self) -> bool:
        """
        :return: True if the solution is a slow solution (`s` after task id in name).
        """
        return self.basename[len(self.task_id)] == 's'

    def is_normal(self) -> bool:
        """
        :return: True if the solution is a normal solution (no `b` or `s` after task id in name).
        """
        return not self.is_bad() and not self.is_slow()
