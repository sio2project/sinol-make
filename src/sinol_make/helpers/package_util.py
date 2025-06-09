import os
import re
import fnmatch
import multiprocessing as mp
from typing import List, Union, Tuple, Type

from sio3pack.files import LocalFile
from sio3pack.test import Test

from sinol_make.commands.inwer.inwer_util import sort_tests
from sinol_make import util
from sinol_make.helpers import paths
from sinol_make.task_type import BaseTaskType
from sinol_make.sio3pack.package import SIO3Package


def get_task_id() -> str:
    return SIO3Package().short_name

def get_groups(tests: List[Test] = None):
    if tests is None:
        tests = SIO3Package().tests
    return sorted(list(set([int(test.group) for test in tests])))


def get_config():
    return SIO3Package().config


def get_solutions_re(task_id: str) -> re.Pattern:
    """
    Returns regex pattern matching all solutions for given task.
    :param task_id: Task id.
    """
    return re.compile(r"^%s[bs]?[0-9]*(_.*)?\.(c|cpp|cc|py)$" % task_id)


def get_executable_key(path_to_exe):
    name = os.path.basename(path_to_exe)
    task_id_len = len(get_task_id())
    value = [0, 0]
    if name[task_id_len] == 's':
        value[0] = 1
        suffix = name.split(".")[0][(task_id_len + 1):]
    elif name[task_id_len] == 'b':
        value[0] = 2
        suffix = name.split(".")[0][(task_id_len + 1):]
    else:
        suffix = name.split(".")[0][task_id_len:]
    if suffix != "":
        i = 0
        digits = ""
        while i < len(suffix) and suffix[i].isdigit():
            digits += suffix[i]
            i += 1
        if digits != "":
            value[1] = int(digits)
    return tuple(value)


def get_matching_tests(tests: List[Test], patterns: List[str]) -> List[Test]:
    """
    Returns list of tests matching given path patterns.
    :param tests: List of all tests available.
    :param patterns: List of patterns to match.
    :return: List of tests with paths matching given path patterns.
    """
    matching_tests = set()
    for pattern in patterns:
        matched_to_pattern = set()
        for test in tests:
            print(test.in_file.path)
            # if absolute path is given, match it directly
            if os.path.isabs(pattern) and fnmatch.fnmatch(test.in_file.path, pattern):
                matched_to_pattern.add(test)
            else:
                # if relative path is given, match it with current working directory
                pattern_relative = os.path.join(os.getcwd(), pattern)
                if fnmatch.fnmatch(test.in_file.path, pattern_relative):
                    matched_to_pattern.add(test)
                else:
                    # if pattern is given, match it with tests filename
                    if fnmatch.fnmatch(os.path.basename(test.in_file.path), pattern):
                        matched_to_pattern.add(test)
        if len(matched_to_pattern) == 0:
            util.warning("Test %s does not exist" % pattern)
        matching_tests.update(matched_to_pattern)

    return list(matching_tests)

def get_matching_files(files: List[LocalFile], patterns: List[str]) -> List[LocalFile]:
    """
    Returns list of files matching given path patterns.
    :param files: List of all files available.
    :param patterns: List of patterns to match.
    :return: List of files with paths matching given path patterns.
    """
    matching_files = set()
    for pattern in patterns:
        matched_to_pattern = set()
        for file in files:
            # if absolute path is given, match it directly
            if os.path.isabs(pattern) and fnmatch.fnmatch(file.path, pattern):
                matched_to_pattern.add(file)
            else:
                # if relative path is given, match it with current working directory
                pattern_relative = os.path.join(os.getcwd(), pattern)
                if fnmatch.fnmatch(file.path, pattern_relative):
                    matched_to_pattern.add(file)
                else:
                    # if pattern is given, match it with filename
                    if fnmatch.fnmatch(os.path.basename(file.path), pattern):
                        matched_to_pattern.add(file)
        if len(matched_to_pattern) == 0:
            util.exit_with_error("File %s does not exist" % pattern)
        matching_files.update(matched_to_pattern)

    return list(matching_files)

def get_tests(arg_tests: Union[List[str], None] = None) -> List[Test]: #Zwracało iny
    """
    Returns list of tests to run.
    :param arg_tests: Tests specified in command line arguments. If None, all tests are returned.
    :return: List of tests to run.
    """
    tests = SIO3Package().tests
    if arg_tests is None:
        return sort_tests(tests)
    else:
        matching_tests = get_matching_tests(tests, arg_tests)
        return sort_tests(matching_tests)


def get_solutions(args_solutions: Union[List[str], None] = None) -> List[LocalFile]:
    """
    Returns list of solutions to run.
    :param args_solutions: Solutions specified in command line arguments. If None, all solutions are returned.
    :return: List of paths of solutions to run.
    """

    solutions = [s.get('file') for s in SIO3Package().model_solutions]
    if args_solutions is None:
        return sorted(solutions, key=lambda solution: get_executable_key(solution.path))
    else:
        matching_solutions = get_matching_files(solutions, args_solutions)
        return sorted(matching_solutions, key=lambda solution: get_executable_key(solution.path))


def get_correct_solution() -> LocalFile:
    """
    Returns path to correct solution.
    :return: Path to correct solution.
    """
    task_id = get_task_id()
    correct_solution = get_solutions([f'{task_id}.*'])
    if len(correct_solution) == 0:
        raise FileNotFoundError("Correct solution not found.")
    return correct_solution[0]


def get_file_name_without_extension(file_path):
    return os.path.splitext(os.path.basename(file_path))[0]


def get_executable(file_path):
    return os.path.basename(file_path) + ".e"


def get_file_lang(file_path):
    return os.path.splitext(file_path)[1][1:].lower()


def get_time_limit(test: Test, lang: str, args=None):
    """
    Returns time limit for given test.
    """
    if args is not None and hasattr(args, "tl") and args.tl is not None:
        return args.tl * 1000

    return SIO3Package().get_time_limit_for_test(test, lang)


def get_memory_limit(test: Test, lang: str, args=None):
    """
    Returns memory limit for given test.
    """
    if args is not None and hasattr(args, "ml") and args.ml is not None:
        return int(args.ml * 1024)

    return SIO3Package().get_memory_limit_for_test(test, lang)


def get_in_tests_re(task_id: str) -> re.Pattern:
    return re.compile(r'^%s(([0-9]+)([a-z]?[a-z0-9]*))\.in$' % re.escape(task_id))


def get_out_tests_re(task_id: str) -> re.Pattern:
    return re.compile(r'^%s(([0-9]+)([a-z]?[a-z0-9]*))\.out$' % re.escape(task_id))


def get_all_code_files() -> List[LocalFile]:
    """
    Returns all code files in package.
    :return: List of code files.
    """
    return [sol["file"] for sol in SIO3Package().model_solutions] + SIO3Package().additional_files


def get_files_matching_pattern(pattern: str) -> List[LocalFile]:
    """
    Returns all files in package matching given pattern.
    :param pattern: Pattern to match.
    :return: List of files matching the pattern.
    """
    all_files = get_all_code_files()
    return [file for file in all_files if fnmatch.fnmatch(os.path.basename(file.path), pattern)]


def any_files_matching_pattern(pattern: str) -> bool:
    """
    Returns True if any file in package matches given pattern.
    :param pattern: Pattern to match.
    :return: True if any file in package matches given pattern.
    """
    return len(get_files_matching_pattern(pattern)) > 0


def check_if_contest_type_changed(contest_type):
    """
    Checks if contest type in cache is different then contest type specified in config.yml.
    :param contest_type: Contest type specified in config.yml.
    :return: True if contest type in cache is different then contest type specified in config.yml.
    """
    if not os.path.isfile(paths.get_cache_path("contest_type")):
        return False
    with open(paths.get_cache_path("contest_type"), "r") as contest_type_file:
        cached_contest_type = contest_type_file.read()
    return cached_contest_type != contest_type


def save_contest_type_to_cache(contest_type):
    """
    Saves contest type to cache.
    :param contest_type: Contest type.
    """
    with open(paths.get_cache_path("contest_type"), "w") as contest_type_file:
        contest_type_file.write(contest_type)


def validate_test(test_path: str) -> Tuple[bool, str]:
    """
    Check if test doesn't contain leading/trailing whitespaces,
    has only one space between tokens and ends with newline.
    Exits with error if any of the conditions is not met.
    :return: Tuple of two values: True if test is valid, error message otherwise.
    """
    basename = os.path.basename(test_path)
    num_empty = 0
    with open(test_path, 'br') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            line = line.decode('utf-8')
            if len(line) > 0 and line[0] == ' ':
                return False, util.error(f'Leading whitespace in {basename}:{i + 1}')
            if len(line) > 0 and (line[-2:] == '\r\n' or line[-2:] == '\n\r' or line[-1] == '\r'):
                return False, util.error(f'Carriage return at the end of {basename}:{i + 1}')
            if len(line) > 0 and line[-1] != '\n':
                return False, util.error(f'No newline at the end of {basename}')
            if line == '\n' or line == '':
                num_empty += 1
                continue
            elif i == len(lines) - 1:
                num_empty = 0
            if line[-2] == ' ':
                return False, util.error(f'Trailing whitespace in {basename}:{i + 1}')
            for j in range(len(line) - 1):
                if line[j] == ' ' and line[j + 1] == ' ':
                    return False, util.error(f'Tokens not separated by one space in {basename}:{i + 1}')

        if num_empty != 0:
            return False, util.error(f'Exactly one empty line expected in {basename}')

    return True, ''


def validate_tests(tests: List[str], cpus: int, type: str = 'input'):
    """
    Validate all tests in parallel.
    """
    if not tests:
        return
    print(f'Validating {type} test contents.')
    num_tests = len(tests)
    finished = 0
    with mp.Pool(cpus) as pool:
        for valid, message in pool.imap(validate_test, tests):
            if not valid:
                util.exit_with_error(message)
            finished += 1
            print(f'Validated {finished}/{num_tests} tests', end='\r')
    print()
    print(util.info(f'All {type} tests are valid!'))


def get_all_inputs() -> List[LocalFile]:
    return [file.in_file for file in SIO3Package().get_tests()]


def get_task_type_cls() -> Type[BaseTaskType]:
    return BaseTaskType.get_task_type()


def get_task_type(timetool_name, timetool_path) -> BaseTaskType:
    task_type_cls = get_task_type_cls()
    return task_type_cls(timetool_name, timetool_path)


def get_out_from_in(test) -> str: #TODO not needed?
    """
    Returns path to output file corresponding to given input file.
    """
    return os.path.join("out", os.path.splitext(os.path.basename(test))[0] + ".out")

def reload_tests():
    """
    Reloads tests from package.
    """
    SIO3Package().reload_tests()
