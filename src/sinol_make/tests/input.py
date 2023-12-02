import re
import os
from typing import List, Union

from sinol_make.tests.test import Test


class InputTest(Test):
    def get_type(self) -> str:
        return "input"

    def get_dir(self) -> str:
        return "in"

    @staticmethod
    def _regex_match_static(task_id: str) -> re.Pattern:
        return re.compile(r'^(%s(([0-9]+)([a-z]?[a-z0-9]*))).in$' % task_id)

    @staticmethod
    def get_all(task_id: str, path=None, arg_tests: Union[List[str], None] = None) -> "List[InputTest]":
        """
        Get all input tests for the task.
        :param task_id: Task ID.
        :param path: Path to the directory with input tests.
        :param arg_tests: Tests specified in command line arguments. If None, all tests are returned.
        :return: List of input tests.
        """
        if path is None:
            path = "in"
        res = []
        if arg_tests is None:
            for file in os.listdir(os.path.abspath(path)):
                basename = os.path.basename(file)
                if InputTest._regex_match_static(task_id).match(basename) is not None:
                    res.append(InputTest(task_id, os.path.join(path, file)))
        else:
            for test in arg_tests:
                basename = os.path.basename(test)
                if InputTest._regex_match_static(task_id).match(basename) is not None and os.path.exists(test):
                    res.append(InputTest(task_id, test))
                if not os.path.isabs(test):
                    alt_test = os.path.join(path, test)
                    if InputTest._regex_match_static(task_id).match(basename) is not None and os.path.exists(alt_test):
                        res.append(InputTest(task_id, alt_test))
        return sorted(res, key=lambda t: (t.group, t.test_id))

    @staticmethod
    def get_group(task_id: str, group: int) -> "List[InputTest]":
        """
        Get all input tests for the task.
        :return: List of input tests.
        """
        res = []
        for file in os.listdir("in"):
            if InputTest._regex_match_static(task_id).match(file) is not None:
                test = InputTest(task_id, file)
                if test.group == group:
                    res.append(test)
        return res
