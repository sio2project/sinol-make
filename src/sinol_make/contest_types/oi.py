import argparse

from sinol_make import util
from sinol_make.helpers import package_util
from sinol_make.structs.status_structs import ExecutionResult
from sinol_make.contest_types.default import DefaultContest


class OIContest(DefaultContest):
    """
    Contest type for Polish Olympiad in Informatics.
    """

    def get_type(self) -> str:
        return "oi"

    def argument_overrides(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Add arguments for features required by OI contest
        """
        args.export_ocen = True
        return args

    def get_test_score(self, result: ExecutionResult, time_limit, memory_limit):
        """
        Full score if took less than half of limit, otherwise linearly decreasing to 1.
        This function is copied from `oioioi` code.
        https://github.com/sio2project/oioioi/blob/40a377d3f2d5cd9c94d01f03e197501ce4aab597/oioioi/programs/utils.py#L107
        """
        if result.Status != 'OK':
            return 0
        if result.Points == 0:
            return 0
        elif result.Time <= time_limit / 2.0:
            return result.Points
        else:
            return 1 + int((result.Points - 1) * ((time_limit - result.Time) / (time_limit / 2.0)))

    def verify_pre_gen(self):
        """
        Verify if scores sum up to 100.
        """
        config = package_util.get_config()
        if 'scores' not in config:
            util.exit_with_error("Scores are not defined in config.yml.")
        total_score = sum(config['scores'].values())
        if total_score != 100:
            util.exit_with_error(f"Total score in config is {total_score}, but should be 100.")

    def allow_per_test_limits(self):
        return False

    def verify_tests_order(self):
        return True
