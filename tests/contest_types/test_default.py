from sinol_make import contest_types
from sinol_make.commands.run import ExecutionResult


def test_get_test_score():
    contest = contest_types.DefaultContest()
    result = ExecutionResult("OK", 0, 0, 42)
    assert contest.get_test_score(result, 1000, 256) == 42


def test_get_group_score():
    contest = contest_types.DefaultContest()
    assert contest.get_group_score([100, 100, 100], 100) == 100
    assert contest.get_group_score([100, 100, 100], 200) == 200
    assert contest.get_group_score([50, 100, 100], 60) == 30
    assert contest.get_group_score([50, 100, 100], 100) == 50
    assert contest.get_group_score([0, 10, 20], 100) == 0
    assert contest.get_group_score([10, 3, 5], 50) == 2


def test_assign_scores():
    contest = contest_types.DefaultContest()
    assert contest.assign_scores([0, 1, 2, 3]) == {0: 0, 1: 33, 2: 33, 3: 34}
    assert contest.assign_scores([1, 2, 3]) == {1: 33, 2: 33, 3: 34}
    assert contest.assign_scores([0, 1, 2]) == {0: 0, 1: 50, 2: 50}


def test_get_possible_score():
    contest = contest_types.DefaultContest()
    assert contest.get_possible_score([0, 1, 2, 3], {0: 0, 1: 33, 2: 33, 3: 34}) == 100
    assert contest.get_possible_score([1, 2, 3], {1: 33, 2: 33, 3: 34}) == 100
    assert contest.get_possible_score([0, 2], {0: 0, 1: 50, 2: 50}) == 50


def test_get_global_score():
    contest = contest_types.DefaultContest()
    assert contest.get_global_score({1: {"points": 10}, 2: {"points": 20}}, 100) == 30
