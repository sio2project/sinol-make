from sinol_make.commands.run.structs import ExecutionResult
from sinol_make.contest_types.default import DefaultContest


class OIContest(DefaultContest):
    """
    Contest type for Polish Olympiad in Informatics.
    """

    def get_test_score(self, result: ExecutionResult, time_limit, memory_limit):
        """Full score if took less than half of limit and then decreasing to 1"""
        if result.Status != 'OK':
            return 0
        elif result.Time <= time_limit / 2.0:
            return 100
        else:
            return 1 + int((result.Points - 1) * ((time_limit - result.Time) / (time_limit / 2.0)))
