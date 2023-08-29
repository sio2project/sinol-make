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
