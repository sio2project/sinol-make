import glob, importlib, os, sys, requests, yaml
import math
import platform
import tarfile
import hashlib
import multiprocessing
import resource
from typing import Union
from packaging.version import parse as parse_version

from sinol_make.contest_types import get_contest_type
from sinol_make.helpers import paths, cache
from sinol_make.helpers.func_cache import cache_result
from sinol_make.structs.status_structs import Status


@cache_result()
def get_commands():
    """
    Function to get an array of all available commands.
    """
    commands_path = glob.glob(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'commands/*'
        )
    )
    commands = []
    for path in commands_path:
        temp = importlib.import_module('sinol_make.commands.' + os.path.basename(path), 'Command')
        commands.append(temp.Command())

    return commands


def get_command_names():
    """
    Function to get an array of all available command names.
    """
    return [command.get_name() for command in get_commands()]


def find_and_chdir_package():
    """
    Checks if current directory or parent directory is a package directory.
    If it is, it changes the current working directory to it and returns True.
    If it isn't, it returns False.
    """
    if os.path.exists(os.path.join(os.getcwd(), 'config.yml')):
        return True
    elif os.path.exists(os.path.join(os.getcwd(), '..', 'config.yml')):
        os.chdir('..')
        return True
    else:
        return False


def init_package_command(args):
    """
    Updates arguments with contest specific overrides for commands
    that require being in package directory
    """
    exit_if_not_package()
    contest = get_contest_type()
    contest.verify_config()
    return contest.argument_overrides(args)


def exit_if_not_package():
    """
    Checks if current directory or parent directory is a package directory.
    If it is, current working directory is changed to it.
    If it isn't, it exits with an error.
    """
    if not find_and_chdir_package():
        exit_with_error('You are not in a package directory (couldn\'t find config.yml in current directory).')
    cache.create_cache_dirs()
    cache.check_can_access_cache()


def save_config(config):
    """
    Function to save nicely formated config.yml.
    """

    # We add the fields in the `config.yml`` in a particular order to make the config more readable.
    # The fields that are not in this list will be appended to the end of the file.
    order = [
        "title",
        "title_pl",
        "title_en",
        "sinol_task_id",
        "sinol_contest_type",
        "sinol_latex_compiler",
        "sinol_static_tests",
        "sinol_undocumented_time_tool",
        "sinol_undocumented_test_limits",
        "num_processes",
        "memory_limit",
        "memory_limits",
        "time_limit",
        "time_limits",
        "override_limits",
        "scores",
        {
            "key": "extra_compilation_files",
            "default_flow_style": None
        },
        {
            "key": "extra_compilation_args",
            "default_flow_style": None
        },
        {
            "key": "extra_execution_files",
            "default_flow_style": None
        },
        {
            "key": "sinol_expected_scores",
            "default_flow_style": None
        },
    ]

    config = config.copy()
    with open("config.yml", "w") as config_file:
        for field in order:
            if isinstance(field, dict): # If the field is a dict, it means that it has a custom property (for example default_flow_style).
                if field["key"] in config:
                    yaml.dump({field["key"]: config[field["key"]]}, config_file, default_flow_style=field["default_flow_style"], allow_unicode=True)
                    # The considered fields are deleted, thus `config` at the end will contain only custom fields written by the user.
                    del config[field["key"]]
            else: # When the field is a string, it doesn't have any custom properties, so it's just a dict key.
                if field in config:
                    yaml.dump({field: config[field]}, config_file, allow_unicode=True)
                    del config[field] # Same reason for deleting as above.

        if config != {}:
            print(warning("Found unknown fields in config.yml: " + ", ".join([str(x) for x in config])))
            # All remaining non-considered fields are appended to the end of the file.
            yaml.dump(config, config_file, allow_unicode=True)


def import_importlib_resources():
    """
    Function to import importlib_resources.
    For Python 3.8 and below, we use importlib_resources.
    For Python 3.9 and above, we use importlib.resources.
    """
    python_version = sys.version_info
    if python_version.minor <= 8:
        import importlib_resources as importlib
    else:
        import importlib.resources as importlib
    return importlib


def is_dev(version):
    """
    Function to check if the version is a development version.
    """
    return parse_version(version).is_devrelease


def check_for_updates(current_version, check=True) -> Union[str, None]:
    """
    Function to check if there is a new version of sinol-make.
    :param current_version: current version of sinol-make
    :param check: whether to check for new version
    :return: returns new version if there is one, None otherwise
    """
    importlib = import_importlib_resources()

    data_dir = importlib.files("sinol_make").joinpath("data")
    if not data_dir.is_dir():
        os.mkdir(data_dir)

    # We check for new version asynchronously, so that it doesn't slow down the program.
    # If the main process exits, the check_version process will also exit.
    if check:
        process = multiprocessing.Process(target=check_version, daemon=True)
        process.start()
    version_file = data_dir.joinpath("version")

    try:
        version = version_file.read_text()
    except (PermissionError, FileNotFoundError):
        try:
            with open(paths.get_cache_path("sinol_make_version"), "r") as f:
                version = f.read()
        except (FileNotFoundError, PermissionError):
            return None

    try:
        if not is_dev(version) and parse_version(version) > parse_version(current_version):
            return version
        if is_dev(current_version) and is_dev(version) and parse_version(version) > parse_version(current_version):
            return version
        else:
            return None
    except ValueError:  # If the version file is corrupted, we just ignore it.
        return None


def check_version():
    """
    Function that asynchronously checks for new version of sinol-make.
    Writes the newest version to data/version file.
    """
    importlib = import_importlib_resources()

    try:
        request = requests.get("https://pypi.python.org/pypi/sinol-make/json", timeout=1)
    except requests.exceptions.RequestException:
        return

    if request.status_code != 200:
        return

    data = request.json()
    versions = list(data["releases"].keys())
    versions.sort(key=parse_version)
    latest_version = versions[-1]

    version_file = importlib.files("sinol_make").joinpath("data/version")
    try:
        version_file.write_text(latest_version)
    except PermissionError:
        if find_and_chdir_package():
            try:
                with open(paths.get_cache_path("sinol_make_version"), "w") as f:
                    f.write(latest_version)
            except PermissionError:
                pass


def lines_diff(lines1, lines2):
    """
    Function to compare two lists of lines.
    Returns True if they are the same, False otherwise.
    """
    if len(lines1) != len(lines2):
        return False

    for i in range(len(lines1)):
        if lines1[i].rstrip() != lines2[i].rstrip():
            return False

    return True


def get_terminal_size():
    """
    Function to get the size of the terminal.
    :return: triple (has_terminal, width, height)
    """
    has_terminal = True
    try:
        terminal_width = os.get_terminal_size().columns
        terminal_height = os.get_terminal_size().lines
    except OSError:
        has_terminal = False
        terminal_width = 80
        terminal_height = 30
    return has_terminal, terminal_width, terminal_height


def get_templates_dir():
    """
    Function to get the path to the templates' directory.
    :return: path to the templates directory
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))


def fix_line_endings(file):
    with open(file, "rb") as f:
        content = f.read()
    with open(file, "wb") as f:
        f.write(content.replace(b"\r\n", b"\n"))


def stringify_keys(d):
    """
    Function to stringify all keys in a dict.
    """
    if isinstance(d, dict):
        return {str(k): stringify_keys(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [stringify_keys(x) for x in d]
    else:
        return d


def change_stack_size_to_unlimited():
    """
    Function to change the stack size to unlimited.
    """
    if is_macos():
        return
    try:
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    except (resource.error, ValueError):
        # We can't run `ulimit -s unlimited` in the code, because since it failed, it probably requires root.
        print(error(f'Failed to change stack size to unlimited. Please run `ulimit -s unlimited` '
                    f'to make sure that solutions with large stack size will work.'))


def is_wsl():
    """
    Function to check if the program is running on Windows Subsystem for Linux.
    """
    return sys.platform == "linux" and "microsoft" in platform.uname().release.lower()


def is_linux():
    """
    Function to check if the program is running on Linux (including WSL).
    """
    return sys.platform == "linux"


def is_macos():
    """
    Function to check if the program is running on macOS.
    """
    return sys.platform == "darwin"


def is_macos_arm():
    """
    Function to check if the program is running on macOS on ARM.
    """
    return is_macos() and platform.machine().lower() == "arm64"


def get_file_md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def try_fix_config(config):
    """
    Function to try to fix the config.yml file.
    Tries to:
    - reformat `sinol_expected_scores` field
    :param config: config.yml file as a dict
    :return: config.yml file as a dict
    """
    # The old format was:
    # sinol_expected_scores:
    #   solution1:
    #     expected: {1: OK, 2: OK, ...}
    #     points: 100
    #
    # We change it to:
    # sinol_expected_scores:
    #   solution1:
    #     expected: {1: {status: OK, points: 100}, 2: {status: OK, points: 100}, ...}
    #     points: 100
    try:
        new_expected_scores = {}
        expected_scores = config["sinol_expected_scores"]
        contest = get_contest_type()
        groups = []
        for solution, results in expected_scores.items():
            for group in results["expected"].keys():
                if group not in groups:
                    groups.append(int(group))

        scores = contest.assign_scores(groups)
        for solution, results in expected_scores.items():
            new_expected_scores[solution] = {"expected": {}, "points": results["points"]}
            for group, result in results["expected"].items():
                if result in Status.possible_statuses():
                    new_expected_scores[solution]["expected"][group] = {"status": result}
                    if result == "OK":
                        new_expected_scores[solution]["expected"][group]["points"] = scores[group]
                    else:
                        new_expected_scores[solution]["expected"][group]["points"] = 0
                else:
                    # This means that the result is probably valid.
                    new_expected_scores[solution]["expected"][group] = result
        config["sinol_expected_scores"] = new_expected_scores
        save_config(config)
    except:
        # If there is an error, we just delete the field.
        if "sinol_expected_scores" in config:
            del config["sinol_expected_scores"]
            save_config(config)
    return config


def extract_tar(tar: tarfile.TarFile, destination: str):
    if sys.version_info.major == 3 and sys.version_info.minor >= 12:
        tar.extractall(destination, filter='tar')
    else:
        tar.extractall(destination)


def default_cpu_count():
    """
    Function to get default number of cpus to use for multiprocessing.
    """
    cpu_count = multiprocessing.cpu_count()
    if cpu_count == 1:
        return 1
    return cpu_count - max(1, int(math.log2(cpu_count)) - 1)


def color_red(text): return "\033[91m{}\033[00m".format(text)
def color_green(text): return "\033[92m{}\033[00m".format(text)
def color_yellow(text): return "\033[93m{}\033[00m".format(text)
def color_gray(text): return "\033[90m{}\033[00m".format(text)
def bold(text): return "\033[01m{}\033[00m".format(text)

def info(text):
    return bold(color_green(text))
def warning(text):
    return bold(color_yellow(text))
def error(text):
    return bold(color_red(text))


def exit_with_error(text, func=None):
    print(error(text))
    try:
        func()
    except TypeError:
        pass
    exit(1)


def has_sanitizer_error(output, exit_code):
    return ('ELF_ET_DYN_BASE' in output or 'ASan' in output) and exit_code != 0
