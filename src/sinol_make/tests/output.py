import re
import os
from typing import List

from sinol_make.tests.test import Test


class OutputTest(Test):
    def get_type(self) -> str:
        return "output"

    def get_dir(self) -> str:
        return "out"

    @staticmethod
    def _regex_match_static(task_id: str) -> re.Pattern:
        return re.compile(r'^(%s(([0-9]+)([a-z]?[a-z0-9]*))).out$' % task_id)

    @staticmethod
    def get_all(task_id: str, path = None) -> "List[OutputTest]":
        """
        Get all input tests for the task.
        :param task_id: Task ID.
        :param path: Path to the directory with input tests.
        :return: List of input tests.
        """
        if path is None:
            path = "out"
        res = []
        for file in os.listdir(os.path.abspath(path)):
            basename = os.path.basename(file)
            if OutputTest._regex_match_static(task_id).match(basename) is not None:
                res.append(OutputTest(task_id, os.path.join(path, file)))
        return sorted(res, key=lambda t: (t.group, t.test_id))

    @staticmethod
    def get_group(task_id: str, group: int) -> "List[OutputTest]":
        """
        Get all input tests for the task.
        :return: List of input tests.
        """
        res = []
        for file in os.listdir("in"):
            if OutputTest._regex_match_static(task_id).match(file) is not None:
                test = OutputTest(task_id, file)
                if test.group == group:
                    res.append(test)
        return res
