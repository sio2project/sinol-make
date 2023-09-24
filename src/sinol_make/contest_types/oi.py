from sinol_make.structs.status_structs import ExecutionResult
from sinol_make.contest_types.default import DefaultContest


class OIContest(DefaultContest):
    """
    Contest type for Polish Olympiad in Informatics.
    """

    def get_test_score(self, result: ExecutionResult, time_limit, memory_limit):
        """
        Full score if took less than half of limit, otherwise linearly decreasing to 1.
        This function is copied from `oioioi` code.
        https://github.com/sio2project/oioioi/blob/40a377d3f2d5cd9c94d01f03e197501ce4aab597/oioioi/programs/utils.py#L107
        """
        if result.Status != 'OK':
            return 0
        elif result.Time <= time_limit / 2.0:
            return 100
        else:
            return 1 + int((result.Points - 1) * ((time_limit - result.Time) / (time_limit / 2.0)))
