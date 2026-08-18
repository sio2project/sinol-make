import os
import re
import yaml
import glob
import fnmatch
import hashlib
import multiprocessing as mp
from enum import Enum
from typing import List, Union, Dict, Any, Tuple, Type

from sinol_make.helpers.func_cache import cache_result
from sinol_make import util, contest_types
from sinol_make.helpers import paths
from sinol_make.task_type import BaseTaskType


@cache_result(cwd=True)
def get_task_id() -> str:
    config = get_config()
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
    return int("".join(re.search(r'\d+', extract_test_id(test_path, task_id)).group()))


def get_groups(tests, task_id):
    return sorted(list(set([get_group(test, task_id) for test in tests])))


def get_test_key(test, task_id):
    return get_group(test, task_id), test


def get_config():
    try:
        with open(os.path.join(os.getcwd(), "config.yml"), "r") as config_file:
            return yaml.load(config_file, Loader=yaml.FullLoader) or {}
    except FileNotFoundError:
        # Potentially redundant with util:exit_if_not_package
        util.exit_with_error("You are not in a package directory (couldn't find config.yml in current directory).")
    except yaml.YAMLError as e:
        util.exit_with_error("config.yml is not a valid YAML. Fix it before continuing:\n" + str(e))


def get_extra_compilation_args(lang: str, config=None) -> List[str]:
    """
    Returns extra compilation arguments for given language.
    Arguments which are files in `prog/` are converted to absolute paths,
    the rest is passed to the compiler as-is.
    :param lang: Language (file extension without the dot), for example `cpp`.
    :param config: Config dict. If None, it is read from `config.yml`.
    """
    if config is None:
        config = get_config()
    args = config.get("extra_compilation_args", {}).get(lang, [])
    if isinstance(args, str):
        args = [args]

    extra_compilation_args = []
    for arg in args:
        path = os.path.join(os.getcwd(), "prog", arg)
        if os.path.exists(path):
            extra_compilation_args.append(path)
        else:
            extra_compilation_args.append(arg)
    return extra_compilation_args


def get_extra_compilation_files(config=None) -> List[str]:
    """
    Returns absolute paths to extra compilation files.
    :param config: Config dict. If None, it is read from `config.yml`.
    """
    if config is None:
        config = get_config()
    return [os.path.join(os.getcwd(), "prog", file) for file in config.get("extra_compilation_files", [])]


# Languages which are compiled together, so that a change to any of them affects
# compilation of the others (for example a header file used by a C++ solution).
COMPILATION_LANG_FAMILIES = {'c': 'cpp', 'cc': 'cpp', 'cpp': 'cpp', 'h': 'cpp', 'hpp': 'cpp'}


def get_extra_compilation_hash(lang: str, extra_compilation_args=None, extra_compilation_files=None) -> str:
    """
    Returns a hash of everything that affects compilation apart from the compiled file itself:
    extra compilation arguments and contents of extra compilation files.
    Thanks to this, changing a library or a compilation flag invalidates the compilation cache.
    :param lang: Language of the compiled file (file extension without the dot), for example `cpp`.
                 Extra compilation files in other languages are ignored.
    :param extra_compilation_args: Extra compilation arguments (as returned by `get_extra_compilation_args`).
    :param extra_compilation_files: Extra compilation files (as returned by `get_extra_compilation_files`).
    :return: Hash of the arguments and files or an empty string if there are none. Empty string is
             returned so that cache created by older versions of sinol-make stays valid for packages
             which don't use them.
    """
    family = COMPILATION_LANG_FAMILIES.get(lang, lang)
    files = [file for file in extra_compilation_files or []
             if COMPILATION_LANG_FAMILIES.get(get_file_lang(file), get_file_lang(file)) == family]
    if not extra_compilation_args and not files:
        return ""

    # Only basenames are used, so that moving the package doesn't invalidate the cache.
    parts = []
    # Order of arguments matters for the compiler, so they are not sorted.
    for arg in extra_compilation_args or []:
        if os.path.isfile(arg):
            parts.append(f'{os.path.basename(arg)}:{util.get_file_md5(arg)}')
        else:
            # The argument is a compilation flag, not a file.
            parts.append(arg)
    # Order of files doesn't matter, but it has to be stable.
    for file in sorted(files, key=os.path.basename):
        if os.path.isfile(file):
            parts.append(f'{os.path.basename(file)}:{util.get_file_md5(file)}')
        else:
            parts.append(f'{os.path.basename(file)}:missing')
    return hashlib.md5('\n'.join(parts).encode('utf-8')).hexdigest()


def get_solutions_re(task_id: str) -> re.Pattern:
    """
    Returns regex pattern matching all solutions for given task.
    :param task_id: Task id.
    """
    return re.compile(r"^%s[bs]?[0-9]*(_.*)?\.(c|cpp|cc|py|rs|dmf)$" % task_id)


def get_executable_key(executable, task_id):
    name = get_file_name(executable)
    task_id_len = len(task_id)
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


def get_files_matching(patterns: List[str], directory: str) -> List[str]:
    """
    Returns list of files matching given patterns.
    If pattern is absolute path, it is returned as is.
    If pattern is relative path, it is searched in current directory and in directory specified as argument.
    :param patterns: List of patterns to match.
    :param directory: Directory to search in.
    :return: List of files matching given patterns.
    """
    files_matching = set()
    for solution in patterns:
        if os.path.isabs(solution):
            files_matching.add(solution)
        else:
            # If solution already has `<directory>/` prefix:
            files_matching.update(glob.glob(os.path.join(os.getcwd(), solution)))
            # If solution does not have `<directory>/` prefix:
            files_matching.update(glob.glob(os.path.join(os.getcwd(), directory, solution)))

    return list(files_matching)


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
        existing_tests = []
        for test in get_files_matching(arg_tests, "in"):
            if not os.path.isfile(test):
                util.exit_with_error("Test %s does not exist" % test)
            if os.path.splitext(test)[1] == ".in":
                existing_tests.append(os.path.join("in", os.path.basename(test)))
        return sorted(existing_tests, key=lambda test: get_test_key(test, task_id))


def get_solutions(task_id: str, args_solutions: Union[List[str], None] = None) -> List[str]:
    """
    Returns list of solutions to run.
    :param task_id: Task id.
    :param args_solutions: Solutions specified in command line arguments. If None, all solutions are returned.
    :return: List of solutions to run.
    """
    solutions_re = get_solutions_re(task_id)
    if args_solutions is None:
        solutions = [solution for solution in os.listdir("prog/")
                     if solutions_re.match(solution)]
        return sorted(solutions, key=lambda solution: get_executable_key(solution, task_id))
    else:
        solutions = []
        for solution in get_files_matching(args_solutions, "prog"):
            if not os.path.isfile(solution):
                util.exit_with_error("Solution %s does not exist" % solution)
            if solutions_re.match(os.path.basename(solution)) is not None:
                solutions.append(os.path.basename(solution))

        return sorted(solutions, key=lambda solution: get_executable_key(solution, task_id))


def get_correct_solution(task_id: str) -> str:
    """
    Returns path to correct solution.
    :param task_id: Task id.
    :return: Path to correct solution.
    """
    correct_solution = get_solutions(task_id, [f'{task_id}.*'])
    if len(correct_solution) == 0:
        raise FileNotFoundError("Correct solution not found.")
    return os.path.join(os.getcwd(), "prog", correct_solution[0])


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


def _get_limit_from_dict(dict: Dict[str, Any], limit_type: LimitTypes, test_id: str, test_group: str, test_path: str,
                         allow_test_limit: bool = False):
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
            if allow_test_limit:
                return dict[plural_limit_name][test_id]
            else:
                util.exit_with_error(
                    f'{os.path.basename(test_path)}: Specifying limit for a single test is not allowed in sinol-make.')
        elif test_group in dict[plural_limit_name]:
            return dict[plural_limit_name][test_group]
    if limit_name in dict:
        return dict[limit_name]
    else:
        return None


def _get_limit(limit_type: LimitTypes, test_path: str, config: Dict[str, Any], lang: str, task_id: str):
    test_id = extract_test_id(test_path, task_id)
    test_group = str(get_group(test_path, task_id))
    contest_type = contest_types.get_contest_type()
    allow_test_limit = config.get("sinol_undocumented_test_limits", False) or contest_type.allow_per_test_limits()
    global_limit = _get_limit_from_dict(config, limit_type, test_id, test_group, test_path, allow_test_limit)
    override_limits_dict = config.get("override_limits", {}).get(lang, {})
    overriden_limit = _get_limit_from_dict(override_limits_dict, limit_type, test_id, test_group, test_path,
                                           allow_test_limit)
    if overriden_limit is not None:
        return overriden_limit
    else:
        if global_limit is not None:
            return global_limit
        else:
            if limit_type == LimitTypes.TIME_LIMIT:
                util.exit_with_error(
                    f'Time limit was not defined for test {os.path.basename(test_path)} in config.yml.')
            elif limit_type == LimitTypes.MEMORY_LIMIT:
                util.exit_with_error(
                    f'Memory limit was not defined for test {os.path.basename(test_path)} in config.yml.')


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


def get_in_tests_re(task_id: str) -> re.Pattern:
    return re.compile(r'^%s(([0-9]+)([a-z]?[a-z0-9]*))\.in$' % re.escape(task_id))


def get_out_tests_re(task_id: str) -> re.Pattern:
    return re.compile(r'^%s(([0-9]+)([a-z]?[a-z0-9]*))\.out$' % re.escape(task_id))


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

    in_test_re = get_in_tests_re(task_id)
    invalid_in_tests = get_invalid_files(os.path.join("in", "*.in"), in_test_re)
    if len(invalid_in_tests) > 0:
        util.exit_with_error(f'Input tests with invalid names: {", ".join(invalid_in_tests)}.')

    out_test_re = get_out_tests_re(task_id)
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
    for ext in ["c", "cpp", "py", "java", "rs", "dmf"]:
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


def get_all_inputs(task_id):
    in_test_re = get_in_tests_re(task_id)
    inputs = []
    for file in glob.glob(os.path.join(os.getcwd(), "in", "*.in")):
        if in_test_re.match(os.path.basename(file)):
            inputs.append(file)
    return inputs


def get_task_type_cls() -> Type[BaseTaskType]:
    return BaseTaskType.get_task_type()


def validate_fake_time(config):
    if 'fake_time' in config:
        allowed = ('off', 'zero', 'random')
        if config['fake_time'] not in allowed:
            util.exit_with_error(
                f'Invalid value for fake_time in config.yml: "{config["fake_time"]}". '
                f'Allowed values: {", ".join(allowed)}.')


def _parse_group_id(group, what):
    """
    Converts a group id from config.yml to an int.
    YAML may parse group ids as either ints or strings, both are accepted.
    """
    try:
        return int(group)
    except (TypeError, ValueError):
        util.exit_with_error(f'subtask_dependencies: {what} \'{group}\' is not a valid group number.')


def get_subtask_dependencies(config) -> Dict[int, List[int]]:
    """
    Returns the `subtask_dependencies` entry from config.yml as a dictionary
    mapping a group to the list of groups it depends on.
    Returns an empty dictionary if the key is not present.
    """
    dependencies = config.get('subtask_dependencies', None)
    if not dependencies:
        return {}
    if not isinstance(dependencies, dict):
        util.exit_with_error(f'subtask_dependencies must be a mapping, got {type(dependencies).__name__}.')

    parsed = {}
    for group, prerequisites in dependencies.items():
        if not isinstance(prerequisites, list):
            util.exit_with_error(f'subtask_dependencies: value for group \'{group}\' must be a list, '
                                 f'got {type(prerequisites).__name__}. Use [{prerequisites}] instead of {prerequisites}.')
        parsed[_parse_group_id(group, 'group')] = [_parse_group_id(prerequisite, 'prerequisite group')
                                                   for prerequisite in prerequisites]
    return parsed


def validate_subtask_dependencies(config, scored_groups=None):
    """
    Validates the `subtask_dependencies` entry in config.yml.
    Checks that group 0 is not used, that there are no circular dependencies and,
    if `scored_groups` is provided, that all referenced groups exist.
    :param config: Config dictionary.
    :param scored_groups: List of groups that have points assigned. If None, group existence is not checked.
    """
    dependencies = get_subtask_dependencies(config)
    if not dependencies:
        return

    if scored_groups is not None:
        scored_groups = sorted(set(int(group) for group in scored_groups))

    for group, prerequisites in dependencies.items():
        for name, checked in [('group', group)] + [('prerequisite group', p) for p in prerequisites]:
            if checked == 0:
                util.exit_with_error(f'subtask_dependencies: {name} \'0\' cannot be used in dependencies, '
                                     f'as group 0 (example tests) is not scored.')
            if scored_groups is not None and checked not in scored_groups:
                util.exit_with_error(f'subtask_dependencies: {name} \'{checked}\' is not a valid scored group. '
                                     f'Valid groups: {scored_groups}.')

    # Detect cycles using DFS.
    visiting = set()
    visited = set()

    def dfs(node):
        visiting.add(node)
        for neighbour in dependencies.get(node, []):
            if neighbour in visiting:
                util.exit_with_error(f'subtask_dependencies: circular dependency detected '
                                     f'involving group \'{neighbour}\'.')
            if neighbour not in visited:
                dfs(neighbour)
        visiting.discard(node)
        visited.add(node)

    for node in dependencies:
        if node not in visited:
            dfs(node)


def get_task_type(timetool_name, timetool_path, fake_time=None) -> BaseTaskType:
    task_type_cls = get_task_type_cls()
    return task_type_cls(timetool_name, timetool_path, fake_time)


def get_out_from_in(test) -> str:
    """
    Returns path to output file corresponding to given input file.
    """
    return os.path.join("out", os.path.splitext(os.path.basename(test))[0] + ".out")
