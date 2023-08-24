from math import ceil
from typing import List

from sinol_make.commands.run.structs import ExecutionResult


class DefaultContest:
    """
    Default contest type.
    Points for tests are equal to points from execution result.
    Group score is equal to minimum score from tests.
    """

    def get_test_score(self, result: ExecutionResult, time_limit, memory_limit):
        return result.Points

    def get_group_score(self, test_scores: List[int], group_max_score):
        min_score = min(test_scores)
        return int(ceil(group_max_score * (min_score / 100.0)))
