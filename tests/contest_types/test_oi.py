from sinol_make import contest_types
from sinol_make.structs.status_structs import ExecutionResult


def test_get_test_score():
    contest = contest_types.OIContest()
    result = ExecutionResult("WA")
    assert contest.get_test_score(result, 10, 100) == 0

    result = ExecutionResult("OK", 1000, Points=100)
    assert contest.get_test_score(result, 2000, 100) == 100

    result = ExecutionResult("OK", 1500, Points=100)
    assert contest.get_test_score(result, 2000, 100) == 50

    result = ExecutionResult("OK", 1999, Points=100)
    assert contest.get_test_score(result, 2000, 100) == 1

    result = ExecutionResult("OK", 1750, Points=42)
    assert contest.get_test_score(result, 2000, 100) == 11

    result = ExecutionResult("OK", 1100, Points=78)
    assert contest.get_test_score(result, 2000, 1000) == 70
