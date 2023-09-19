import os
import re
import yaml
import glob
import fnmatch
from enum import Enum
from typing import List, Union, Dict, Any

from sinol_make import util
from sinol_make.helpers import paths


def get_task_id() -> str:
    with open(os.path.join(os.getcwd(), "config.yml")) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    if "sinol_task_id" in config:
        return config["sinol_task_id"]
    else:
        print(util.warning("sinol_task_id not specified in config.yml. Using task id from directory name."))
        task_id = os.path.split(os.getcwd())[-1]
        if len(task_id) == 3:
            return task_id
        else:
            util.exit_with_error("Invalid task id. Task id should be 3 characters long.")


def extract_test_id(test_path, task_id):
    """
    Extracts test group and number from test path.
    For example for test abc1a.in it returns 1a.
    :param test_path: Path to test file.
    :param task_id: Task id.
    :return: Test group and number.
    """
    return os.path.split(os.path.splitext(test_path)[0])[1][len(task_id):]


def get_group(test_path, task_id):
    if extract_test_id(test_path, task_id).endswith("ocen"):
        return 0
    return int("".join(filter(str.isdigit, extract_test_id(test_path, task_id))))


def get_test_key(test, task_id):
    return get_group(test, task_id), test


def get_tests(task_id: str, arg_tests: Union[List[str], None] = None) -> List[str]:
    """
    Returns list of tests to run.
    :param task_id: Task id.
    :param arg_tests: Tests specified in command line arguments. If None, all tests are returned.
    :return: List of tests to run.
    """
    if arg_tests is None:
        all_tests = ["in/%s" % test for test in os.listdir("in/")
                     if test[-3:] == ".in"]
        return sorted(all_tests, key=lambda test: get_test_key(test, task_id))
    else:
        return sorted(list(set(arg_tests)), key=lambda test: get_test_key(test, task_id))


def get_file_name(file_path):
    return os.path.split(file_path)[1]


def get_file_name_without_extension(file_path):
    return os.path.splitext(get_file_name(file_path))[0]


def get_executable(file_path):
    return os.path.basename(file_path) + ".e"


def get_executable_path(solution: str) -> str:
    """
    Returns path to compiled executable for given solution.
    """
    return paths.get_executables_path(get_executable(solution))


def get_file_lang(file_path):
    return os.path.splitext(file_path)[1][1:].lower()


class LimitTypes(Enum):
    TIME_LIMIT = 1
    MEMORY_LIMIT = 2


def _get_limit_from_dict(dict: Dict[str, Any], limit_type: LimitTypes, test_id: str, test_group: str, test_path: str):
    if limit_type == LimitTypes.TIME_LIMIT:
        limit_name = "time_limit"
        plural_limit_name = "time_limits"
    elif limit_type == LimitTypes.MEMORY_LIMIT:
        limit_name = "memory_limit"
        plural_limit_name = "memory_limits"
    else:
        raise ValueError("Invalid limit type.")

    if plural_limit_name in dict:
        if test_id in dict[plural_limit_name] and test_id != "0":
            util.exit_with_error(f'{os.path.basename(test_path)}: Specifying limit for single test is a bad practice and is not supported.')
        elif test_group in dict[plural_limit_name]:
            return dict[plural_limit_name][test_group]
    if limit_name in dict:
        return dict[limit_name]
    else:
        return None


def _get_limit(limit_type: LimitTypes, test_path: str, config: Dict[str, Any], lang: str, task_id: str):
    test_id = extract_test_id(test_path, task_id)
    test_group = str(get_group(test_path, task_id))
    global_limit = _get_limit_from_dict(config, limit_type, test_id, test_group, test_path)
    override_limits_dict = config.get("override_limits", {}).get(lang, {})
    overriden_limit = _get_limit_from_dict(override_limits_dict, limit_type, test_id, test_group, test_path)
    if overriden_limit is not None:
        return overriden_limit
    else:
        if global_limit is not None:
            return global_limit
        else:
            if limit_type == LimitTypes.TIME_LIMIT:
                util.exit_with_error(f'Time limit was not defined for test {os.path.basename(test_path)} in config.yml.')
            elif limit_type == LimitTypes.MEMORY_LIMIT:
                util.exit_with_error(f'Memory limit was not defined for test {os.path.basename(test_path)} in config.yml.')


def get_time_limit(test_path, config, lang, task_id, args=None):
    """
    Returns time limit for given test.
    """
    if args is not None and hasattr(args, "tl") and args.tl is not None:
        return args.tl * 1000

    str_config = util.stringify_keys(config)
    return _get_limit(LimitTypes.TIME_LIMIT, test_path, str_config, lang, task_id)


def get_memory_limit(test_path, config, lang, task_id, args=None):
    """
    Returns memory limit for given test.
    """
    if args is not None and hasattr(args, "ml") and args.ml is not None:
        return int(args.ml * 1024)

    str_config = util.stringify_keys(config)
    return _get_limit(LimitTypes.MEMORY_LIMIT, test_path, str_config, lang, task_id)


def validate_test_names(task_id):
    """
    Checks if all files in the package have valid names.
    """
    def get_invalid_files(path, pattern):
        invalid_files = []
        for file in glob.glob(os.path.join(os.getcwd(), path)):
            if not pattern.match(os.path.basename(file)):
                invalid_files.append(os.path.basename(file))
        return invalid_files

    in_test_re = re.compile(r'^(%s(([0-9]+)([a-z]?[a-z0-9]*))).in$' % (re.escape(task_id)))
    invalid_in_tests = get_invalid_files(os.path.join("in", "*.in"), in_test_re)
    if len(invalid_in_tests) > 0:
        util.exit_with_error(f'Input tests with invalid names: {", ".join(invalid_in_tests)}.')

    out_test_re = re.compile(r'^(%s(([0-9]+)([a-z]?[a-z0-9]*))).out$' % (re.escape(task_id)))
    invalid_out_tests = get_invalid_files(os.path.join("out", "*.out"), out_test_re)
    if len(invalid_out_tests) > 0:
        util.exit_with_error(f'Output tests with invalid names: {", ".join(invalid_out_tests)}.')


def get_all_code_files(task_id: str) -> List[str]:
    """
    Returns all code files in package.
    :param task_id: Task id.
    :return: List of code files.
    """
    result = glob.glob(os.path.join(os.getcwd(), "prog", f"{task_id}ingen.sh"))
    for ext in ["c", "cpp", "py", "java"]:
        result += glob.glob(os.path.join(os.getcwd(), f"prog/{task_id}*.{ext}"))
    return result


def get_files_matching_pattern(task_id: str, pattern: str) -> List[str]:
    """
    Returns all files in package matching given pattern.
    :param task_id: Task id.
    :param pattern: Pattern to match.
    :return: List of files matching the pattern.
    """
    all_files = get_all_code_files(task_id)
    return [file for file in all_files if fnmatch.fnmatch(os.path.basename(file), pattern)]


def any_files_matching_pattern(task_id: str, pattern: str) -> bool:
    """
    Returns True if any file in package matches given pattern.
    :param task_id: Task id.
    :param pattern: Pattern to match.
    :return: True if any file in package matches given pattern.
    """
    return len(get_files_matching_pattern(task_id, pattern)) > 0
