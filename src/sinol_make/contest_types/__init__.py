from sinol_make.contest_types.default import DefaultContest
from sinol_make.contest_types.icpc import ICPCContest
from sinol_make.contest_types.oi import OIContest
from sinol_make.contest_types.talent import TalentContest
from sinol_make.helpers.package_util import get_config
from sinol_make.interfaces.Errors import UnknownContestType


def get_contest_type():
    config = get_config()
    contest_type = config.get("sinol_contest_type", "talent").lower()

    if contest_type == "default":
        return DefaultContest()
    elif contest_type == "oi":
        return OIContest()
    elif contest_type == "icpc":
        return ICPCContest()
    elif contest_type == "talent":
        return TalentContest()
    else:
        raise UnknownContestType(f'Unknown contest type "{contest_type}"')
