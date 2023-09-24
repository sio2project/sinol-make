import os
import yaml

from sinol_make.contest_types.default import DefaultContest
from sinol_make.contest_types.icpc import ICPCContest
from sinol_make.contest_types.oi import OIContest
from sinol_make.interfaces.Errors import UnknownContestType


def get_contest_type():
    with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        contest_type = config.get("sinol_contest_type", "default").lower()

    if contest_type == "default":
        return DefaultContest()
    elif contest_type == "oi":
        return OIContest()
    elif contest_type == "icpc":
        return ICPCContest()
    else:
        raise UnknownContestType(f'Unknown contest type "{contest_type}"')
