import argparse

from sinol_make import util
from sinol_make.helpers import package_util
from sinol_make.contest_types.default import DefaultContest


class OIJContest(DefaultContest):
    """
    Contest type for Polish Junior Olympiad in Informatics.
    """

    def get_type(self) -> str:
        return "oij"

    def argument_overrides(self, args: argparse.Namespace) -> argparse.Namespace:
        """
        Add arguments for features required by OIJ contest
        """
        args.export_ocen = True
        return args

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

    def verify_tests_order(self):
        return True
