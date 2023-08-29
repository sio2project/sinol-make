import os
from typing import List, Union

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


def get_time_limit(test_path, config, args=None):
    """
    Returns time limit for given test.
    """
    if args is not None and hasattr(args, "tl") and args.tl is not None:
        return args.tl * 1000

    str_config = util.stringify_keys(config)
    test_id = extract_test_id(test_path)
    test_group = str(get_group(test_path))

    if "time_limits" in str_config:
        if test_id in str_config["time_limits"]:
            return str_config["time_limits"][test_id]
        elif test_group in str_config["time_limits"]:
            return str_config["time_limits"][test_group]
    return str_config["time_limit"]


def get_memory_limit(test_path, config, args=None):
    """
    Returns memory limit for given test.
    """
    if args is not None and hasattr(args, "ml") and args.ml is not None:
        return int(args.ml * 1024)

    str_config = util.stringify_keys(config)
    test_id = extract_test_id(test_path)
    test_group = str(get_group(test_path))

    if "memory_limits" in str_config:
        if test_id in str_config["memory_limits"]:
            return str_config["memory_limits"][test_id]
        elif test_group in str_config["memory_limits"]:
            return str_config["memory_limits"][test_group]
    return str_config["memory_limit"]
