import argparse

from sinol_make.contest_types import DefaultContest
from sinol_make.structs.status_structs import ExecutionResult


class TalentContest(DefaultContest):
    """
    Traditional talent contest
    """

    def argument_overrides(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Add arguments for features required by Talent contest
        """
        args.export_ocen = True
        return args

    def get_test_score(self, result: ExecutionResult, time_limit, memory_limit) -> int:
        if result.Status != 'OK':
            return 0
        elif result.Time <= time_limit / 2.0:
            return result.Points
        else:
            return 1 + int((result.Points - 1) * ((time_limit - result.Time) / (time_limit / 2.0)))
