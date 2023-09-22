import os
from typing import Dict

import yaml

from sinol_make import util
from sinol_make.helpers import paths


def create_compilation_cache():
    os.makedirs(paths.get_cache_path("md5sums"), exist_ok=True)


def get_cache_file(solution_path: str):
    """
    Returns content of cache file for given solution
    :param solution_path: Path to solution
    :return: Content of cache file
    """
    create_compilation_cache()
    try:
        with open(paths.get_cache_path("md5sums", os.path.basename(solution_path)), 'r') as cache_file:
            return yaml.load(cache_file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        return {}


def write_cache_file(solution_path: str, contents: Dict):
    """
    Writes contents to cache file for given solution
    :param solution_path: Path to solution
    :param contents: Contents to write
    """
    create_compilation_cache()
    with open(paths.get_cache_path("md5sums", os.path.basename(solution_path)), 'w') as cache_file:
        yaml.dump(contents, cache_file)


def check_compiled(file_path: str):
    """
    Check if a file is compiled
    :param file_path: Path to the file
    :return: executable path if compiled, None otherwise
    """
    md5sum = util.get_file_md5(file_path)
    try:
        info = get_cache_file(file_path)
        if info.get("md5sum", "") == md5sum:
            exe_path = info.get("executable_path", "")
            if os.path.exists(exe_path):
                return exe_path
        return None
    except FileNotFoundError:
        return None


def save_compiled(file_path: str, exe_path: str):
    """
    Save the compiled executable path to cache in `.cache/md5sums/<basename of file_path>`,
    which contains the md5sum of the file and the path to the executable.
    :param file_path: Path to the file
    :param exe_path: Path to the compiled executable
    """
    write_cache_file(file_path, {
        "md5sum": util.get_file_md5(file_path),
        "executable_path": exe_path
    })
