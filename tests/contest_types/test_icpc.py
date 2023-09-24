from sinol_make import contest_types


def test_assign_scores():
    contest = contest_types.ICPCContest()
    assert contest.assign_scores([0, 1, 2, 3]) == {0: 1, 1: 1, 2: 1, 3: 1}
    assert contest.assign_scores([1, 2, 3]) == {1: 1, 2: 1, 3: 1}
    assert contest.assign_scores([0, 1, 2]) == {0: 1, 1: 1, 2: 1}


def test_get_group_score():
    contest = contest_types.ICPCContest()
    assert contest.get_group_score([1, 1, 1, 1], 1) == 1
    assert contest.get_group_score([1, 0, 1], 1) == 0


def test_get_global_score():
    contest = contest_types.ICPCContest()
    assert contest.get_global_score({1: {"points": 1}, 2: {"points": 1}}, 1) == 1
    assert contest.get_global_score({1: {"points": 1}, 2: {"points": 0}}, 1) == 0
