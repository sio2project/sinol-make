from sinol_make.contest_types.default import DefaultContest
from sinol_make.contest_types.icpc import ICPCContest
from sinol_make.contest_types.oi import OIContest
from sinol_make.contest_types.oij import OIJContest
from sinol_make.helpers.func_cache import cache_result
from sinol_make.helpers.package_util import get_config
from sinol_make.interfaces.Errors import UnknownContestType


@cache_result(cwd=True)
def get_contest_type():
    config = get_config()
    contest_type = config.get("sinol_contest_type", "default").lower()

    if contest_type == "default":
        return DefaultContest()
    elif contest_type == "oi":
        return OIContest()
    elif contest_type == "icpc":
        return ICPCContest()
    elif contest_type == "oij":
        return OIJContest()
    else:
        raise UnknownContestType(f'Unknown contest type "{contest_type}"')
