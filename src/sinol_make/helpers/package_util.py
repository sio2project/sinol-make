import os


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
    return int("".join(filter(str.isdigit, extract_test_id(test_path))))


def get_test_key(test):
    return get_group(test), test


def get_tests(arg_tests: list[str] or None) -> list[str]:
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
