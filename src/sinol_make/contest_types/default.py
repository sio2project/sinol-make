from math import ceil
from typing import List, Dict

from sinol_make import util
from sinol_make.structs.status_structs import ExecutionResult


class DefaultContest:
    """
    Default contest type.
    Points for tests are equal to points from execution result.
    Group score is equal to minimum score from tests.
    Global score is sum of group scores.
    Scores for groups are assigned equally.
    Max possible score is sum of group scores.
    """

    def assign_scores(self, groups: List[int]) -> Dict[int, int]:
        """
        Returns dictionary with scores for each group.
        Called if `scores` is not specified in config.
        :param groups: List of groups
        :return: Dictionary: {"<group>": <points>}
        """
        print(util.warning('Scores are not defined in config.yml. Points will be assigned equally to all groups.'))
        num_groups = len(groups)
        scores = {}
        if groups[0] == 0:
            num_groups -= 1
            scores[0] = 0

        # This only happens when running only on group 0.
        if num_groups == 0:
            return scores

        points_per_group = 100 // num_groups
        for group in groups:
            if group == 0:
                continue
            scores[group] = points_per_group

        if points_per_group * num_groups != 100:
            scores[groups[-1]] += 100 - points_per_group * num_groups

        print("Points will be assigned as follows:")
        total_score = 0
        for group in scores:
            print("%2d: %3d" % (group, scores[group]))
            total_score += scores[group]
        print()
        return scores

    def get_possible_score(self, groups: List[int], scores: Dict[int, int]) -> int:
        """
        Get the maximum possible score.
        :param groups: List of groups.
        :param scores: Dictionary: {"<group>": <points>}
        :return: Maximum possible score.
        """
        if groups[0] == 0 and len(groups) == 1:
            return 0

        possible_score = 0
        for group in groups:
            possible_score += scores[group]
        return possible_score

    def get_test_score(self, result: ExecutionResult, time_limit, memory_limit) -> int:
        """
        Returns points for test.
        :param result: result of execution
        :param time_limit: time limit for test
        :param memory_limit: memory limit for test
        :return: points for test
        """
        return result.Points

    def get_group_score(self, test_scores: List[int], group_max_score) -> int:
        """
        Calculates group score based on tests scores.
        :param test_scores: List of scores for tests
        :param group_max_score: Maximum score for group
        :return:
        """
        min_score = min(test_scores)
        return int(ceil(group_max_score * (min_score / 100.0)))

    def get_global_score(self, groups_scores: Dict[int, Dict], global_max_score) -> int:
        """
        Calculates global score based on groups scores.
        :param groups_scores: Dictionary: {"<group>: {"status": Status, "points": <points for group>}
        :param global_max_score: Maximum score for contest
        :return: Global score
        """
        return sum(group["points"] for group in groups_scores.values())
