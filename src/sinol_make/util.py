import glob, importlib, os, sys, requests, yaml
import platform
import tempfile
import shutil
import hashlib
import subprocess
import threading
import resource
from typing import Union

import sinol_make


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


def check_if_package():
    """
    Function to check if current directory is a package
    """

    cwd = os.getcwd()
    if os.path.exists(os.path.join(cwd, 'config.yml')):
        return True
    return False


def exit_if_not_package():
    """
    Function that exits if current directory is not a package
    """
    if not check_if_package():
        exit_with_error('You are not in a package directory (couldn\'t find config.yml in current directory).')


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
            "key": "sinol_expected_scores",
            "default_flow_style": None
        }
    ]

    config = config.copy()
    with open("config.yml", "w") as config_file:
        for field in order:
            if isinstance(field, dict): # If the field is a dict, it means that it has a custom property (for example default_flow_style).
                if field["key"] in config:
                    yaml.dump({field["key"]: config[field["key"]]}, config_file, default_flow_style=field["default_flow_style"])
                    # The considered fields are deleted, thus `config` at the end will contain only custom fields written by the user.
                    del config[field["key"]]
            else: # When the field is a string, it doesn't have any custom properties, so it's just a dict key.
                if field in config:
                    yaml.dump({field: config[field]}, config_file)
                    del config[field] # Same reason for deleting as above.

        if config != {}:
            print(warning("Found unknown fields in config.yml: " + ", ".join([str(x) for x in config])))
            # All remaining non-considered fields are appended to the end of the file.
            yaml.dump(config, config_file)


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


def check_for_updates(current_version) -> Union[str, None]:
    """
    Function to check if there is a new version of sinol-make.
    :param current_version: current version of sinol-make
    :return: returns new version if there is one, None otherwise
    """
    importlib = import_importlib_resources()

    data_dir = importlib.files("sinol_make").joinpath("data")
    if not data_dir.is_dir():
        os.mkdir(data_dir)

    # We check for new version asynchronously, so that it doesn't slow down the program.
    thread = threading.Thread(target=check_version)
    thread.start()
    version_file = data_dir.joinpath("version")

    if version_file.is_file():
        version = version_file.read_text()
        try:
            if compare_versions(current_version, version) == -1:
                return version
            else:
                return None
        except ValueError:  # If the version file is corrupted, we just ignore it.
            return None
    else:
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
    latest_version = data["info"]["version"]

    version_file = importlib.files("sinol_make").joinpath("data/version")
    version_file.write_text(latest_version)


def compare_versions(version_a, version_b):
    """
    Function to compare two versions.
    Returns 1 if version_a > version_b, 0 if version_a == version_b, -1 if version_a < version_b.
    """

    def convert(version):
        return tuple(map(int, version.split(".")))

    version_a = convert(version_a)
    version_b = convert(version_b)

    if version_a > version_b:
        return 1
    elif version_a == version_b:
        return 0
    else:
        return -1


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


def file_diff(file1_path, file2_path):
    """
    Function to compare two files.
    Returns True if they are the same, False otherwise.
    """
    with open(file1_path) as file1, open(file2_path) as file2:
        return lines_diff(file1.readlines(), file2.readlines())


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
    Function to check if the program is running on Linux and not WSL.
    """
    return sys.platform == "linux" and not is_wsl()


def get_file_md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


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
