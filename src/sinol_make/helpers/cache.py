import os
import yaml
from typing import Union

from sinol_make import util
from sinol_make.structs.cache_structs import CacheFile
from sinol_make.helpers import paths


def get_cache_file(solution_path: str) -> CacheFile:
    """
    Returns content of cache file for given solution
    :param solution_path: Path to solution
    :return: Content of cache file
    """
    os.makedirs(paths.get_cache_path("md5sums"), exist_ok=True)
    try:
        with open(paths.get_cache_path("md5sums", os.path.basename(solution_path)), 'r') as cache_file:
            print(cache_file.read()) # For debugging workflow
        with open(paths.get_cache_path("md5sums", os.path.basename(solution_path)), 'r') as cache_file:
            data = yaml.load(cache_file, Loader=yaml.FullLoader)
            print(data) # For debugging workflow
            return CacheFile.from_dict(data)
    except FileNotFoundError:
        return CacheFile()


def check_compiled(file_path: str) -> Union[str, None]:
    """
    Check if a file is compiled
    :param file_path: Path to the file
    :return: executable path if compiled, None otherwise
    """
    md5sum = util.get_file_md5(file_path)
    try:
        info = get_cache_file(file_path)
        if info.md5sum == md5sum:
            exe_path = info.executable_path
            if os.path.exists(exe_path):
                return exe_path
        return None
    except FileNotFoundError:
        return None


def save_compiled(file_path: str, exe_path: str, is_checker: bool = False):
    """
    Save the compiled executable path to cache in `.cache/md5sums/<basename of file_path>`,
    which contains the md5sum of the file and the path to the executable.
    :param file_path: Path to the file
    :param exe_path: Path to the compiled executable
    :param is_checker: Whether the compiled file is a checker. If True, all cached tests are removed.
    """
    print(file_path, exe_path, is_checker) # For debugging workflow
    info = get_cache_file(file_path)
    info.executable_path = exe_path
    info.md5sum = util.get_file_md5(file_path)
    info.save(file_path)

    if is_checker:
        for solution in os.listdir(paths.get_cache_path('md5sums')):
            info = get_cache_file(solution)
            info.tests = {}
            info.save(solution)
