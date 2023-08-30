import os
from enum import Enum
from typing import List, Union, Dict, Any

from sinol_make import util


def get_task_id() -> str:
    return os.path.split(os.getcwd())[-1]


def extract_test_id(test_path):
    """
    Extracts test group and number from test path.
    For example for test abc1a.in it returns 1a.
    :param test_path: Path to test file.
    :return: Test group and number.
    """
    return os.path.split(os.path.splitext(test_path)[0])[1][3:]


def get_group(test_path):
    if extract_test_id(test_path).endswith("ocen"):
        return 0
    return int("".join(filter(str.isdigit, extract_test_id(test_path))))


def get_test_key(test):
    return get_group(test), test


def get_tests(arg_tests: Union[List[str], None] = None) -> List[str]:
    """
    Returns list of tests to run.
    :param arg_tests: Tests specified in command line arguments. If None, all tests are returned.
    :return: List of tests to run.
    """
    if arg_tests is None:
        all_tests = ["in/%s" % test for test in os.listdir("in/")
                     if test[-3:] == ".in"]
        return sorted(all_tests, key=get_test_key)
    else:
        return sorted(list(set(arg_tests)), key=get_test_key)


def get_file_name(file_path):
    return os.path.split(file_path)[1]


def get_file_name_without_extension(file_path):
    return os.path.splitext(get_file_name(file_path))[0]


def get_executable(file_path):
    return get_file_name_without_extension(file_path) + ".e"


def get_executable_path(solution: str) -> str:
    """
    Returns path to compiled executable for given solution.
    """
    return os.path.join(os.getcwd(), 'cache', 'executables', get_executable(solution))


def get_file_lang(file_path):
    return os.path.splitext(file_path)[1][1:].lower()


class LimitTypes(Enum):
    TIME_LIMIT = 1
    MEMORY_LIMIT = 2


def _get_limit_from_dict(dict: Dict[str, Any], limit_type: LimitTypes, test_id: str, test_group: str):
    if limit_type == LimitTypes.TIME_LIMIT:
        limit_name = "time_limit"
        plural_limit_name = "time_limits"
    elif limit_type == LimitTypes.MEMORY_LIMIT:
        limit_name = "memory_limit"
        plural_limit_name = "memory_limits"
    else:
        raise ValueError("Invalid limit type.")

    if plural_limit_name in dict:
        if test_id in dict[plural_limit_name]:
            util.exit_with_error("Specifying limit for single test is a bad practice and is not supported.")
        elif test_group in dict[plural_limit_name]:
            return dict[plural_limit_name][test_group]
    if limit_name in dict:
        return dict[limit_name]
    else:
        return None


def _get_limit(limit_type: LimitTypes, test_path: str, config: Dict[str, Any], lang: str):
    test_id = extract_test_id(test_path)
    test_group = str(get_group(test_path))
    global_limit = _get_limit_from_dict(config, limit_type, test_id, test_group)
    override_limits_dict = config.get("override_limits", {}).get(lang, {})
    overriden_limit = _get_limit_from_dict(override_limits_dict, limit_type, test_id, test_group)
    if overriden_limit is not None:
        return overriden_limit
    else:
        return global_limit


def get_time_limit(test_path, config, lang, args=None):
    """
    Returns time limit for given test.
    """
    if args is not None and hasattr(args, "tl") and args.tl is not None:
        return args.tl * 1000

    str_config = util.stringify_keys(config)
    return _get_limit(LimitTypes.TIME_LIMIT, test_path, str_config, lang)


def get_memory_limit(test_path, config, lang, args=None):
    """
    Returns memory limit for given test.
    """
    if args is not None and hasattr(args, "ml") and args.ml is not None:
        return int(args.ml * 1024)

    str_config = util.stringify_keys(config)
    return _get_limit(LimitTypes.MEMORY_LIMIT, test_path, str_config, lang)
