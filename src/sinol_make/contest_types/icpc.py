from typing import List, Dict

from sinol_make.structs.status_structs import ExecutionResult
from sinol_make.contest_types import DefaultContest
from sinol_make.structs.status_structs import Status


class ICPCContest(DefaultContest):
    """
    Contest type for ACM ICPC type contest.
    The possible score for one solution is 1 or 0.
    The score is 0 if any of the tests fail.
    """

    def assign_scores(self, groups: List[int]) -> Dict[int, int]:
        return {group: 1 for group in groups}

    def get_possible_score(self, groups: List[int], scores: Dict[int, int]) -> int:
        return 1

    def get_test_score(self, result: ExecutionResult, time_limit, memory_limit):
        if result.Status == Status.OK:
            return 1
        else:
            return 0

    def get_group_score(self, test_scores, group_max_score):
        return min(test_scores)

    def get_global_score(self, groups_scores: Dict[int, Dict], global_max_score):
        return min(group["points"] for group in groups_scores.values())
