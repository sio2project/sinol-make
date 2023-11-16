import os
import yaml
from typing import Union

from sinol_make import util
from sinol_make.structs.cache_structs import CacheFile
from sinol_make.helpers import paths, package_util


def get_cache_file(solution_path: str) -> CacheFile:
    """
    Returns content of cache file for given solution
    :param solution_path: Path to solution
    :return: Content of cache file
    """
    os.makedirs(paths.get_cache_path("md5sums"), exist_ok=True)
    cache_file_path = paths.get_cache_path("md5sums", os.path.basename(solution_path))
    try:
        with open(cache_file_path, 'r') as cache_file:
            data = yaml.load(cache_file, Loader=yaml.FullLoader)
            if not isinstance(data, dict):
                print(util.warning(f"Cache file for program {os.path.basename(solution_path)} is corrupted."))
                os.unlink(cache_file_path)
                return CacheFile()
            try:
                return CacheFile.from_dict(data)
            except ValueError as exc:
                print(util.error(f"An error occured while parsing cache file for solution {os.path.basename(solution_path)}."))
                util.exit_with_error(str(exc))
    except FileNotFoundError:
        return CacheFile()
    except (yaml.YAMLError, TypeError):
        print(util.warning(f"Cache file for program {os.path.basename(solution_path)} is corrupted."))
        os.unlink(cache_file_path)
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
    info = CacheFile()
    info.executable_path = exe_path
    info.md5sum = util.get_file_md5(file_path)
    info.save(file_path)

    if is_checker:
        remove_results_cache()


def save_to_cache_extra_compilation_files(extra_compilation_files, task_id):
    """
    Checks if extra compilation files have changed and saves them to cache.
    If they have, removes all cached solutions that use them.
    :param extra_compilation_files: List of extra compilation files
    :param task_id: Task id
    """
    solutions_re = package_util.get_solutions_re(task_id)
    for file in extra_compilation_files:
        file_path = os.path.join(os.getcwd(), "prog", file)
        if not os.path.exists(file_path):
            continue
        md5sum = util.get_file_md5(file_path)
        lang = package_util.get_file_lang(file)
        if lang == 'h':
            lang = 'cpp'
        info = get_cache_file(file_path)

        if info.md5sum != md5sum:
            for solution in os.listdir(paths.get_cache_path('md5sums')):
                # Remove only files in the same language and matching the solution regex
                if package_util.get_file_lang(solution) == lang and \
                        solutions_re.match(solution) is not None:
                    os.unlink(paths.get_cache_path('md5sums', solution))

        info.md5sum = md5sum
        info.save(file_path)


def remove_results_cache():
    """
    Removes all cached test results
    """
    for solution in os.listdir(paths.get_cache_path('md5sums')):
        info = get_cache_file(solution)
        info.tests = {}
        info.save(solution)


def remove_results_if_contest_type_changed(contest_type):
    """
    Checks if contest type has changed and removes all cached test results if it has.
    :param contest_type: Contest type
    """
    if package_util.check_if_contest_type_changed(contest_type):
        remove_results_cache()
    package_util.save_contest_type_to_cache(contest_type)


def check_can_access_cache():
    """
    Checks if user can access cache.
    """
    try:
        os.makedirs(paths.get_cache_path(), exist_ok=True)
        with open(paths.get_cache_path("test"), "w") as f:
            f.write("test")
        os.unlink(paths.get_cache_path("test"))
    except PermissionError:
        util.exit_with_error("You don't have permission to access the `.cache/` directory. "
                             "`sinol-make` needs to be able to write to this directory.")
