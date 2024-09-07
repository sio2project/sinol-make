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


def check_compiled(file_path: str, compilation_flags: str, sanitizers: bool) -> Union[str, None]:
    """
    Check if a file is compiled
    :param file_path: Path to the file
    :return: executable path if compiled, None otherwise
    """
    md5sum = util.get_file_md5(file_path)
    try:
        info = get_cache_file(file_path)
        if info.md5sum == md5sum and info.compilation_flags == compilation_flags and info.sanitizers == sanitizers:
            exe_path = info.executable_path
            if os.path.exists(exe_path):
                return exe_path
        return None
    except FileNotFoundError:
        return None


def save_compiled(file_path: str, exe_path: str, compilation_flags: str, sanitizers: bool, clear_cache: bool = False):
    """
    Save the compiled executable path to cache in `.cache/md5sums/<basename of file_path>`,
    which contains the md5sum of the file and the path to the executable.
    :param file_path: Path to the file
    :param exe_path: Path to the compiled executable
    :param compilation_flags: Compilation flags used
    :param sanitizers: Whether -fsanitize=undefined,address was used
    :param clear_cache: Set to True if you want to delete all cached test results.
    """
    info = CacheFile(util.get_file_md5(file_path), exe_path, compilation_flags, sanitizers)
    info.save(file_path)
    if clear_cache:
        remove_results_cache()


def _check_file_changed(file_path, lang, task_id):
    solutions_re = package_util.get_solutions_re(task_id)
    md5sum = util.get_file_md5(file_path)
    info = get_cache_file(file_path)

    if info.md5sum != md5sum:
        for solution in os.listdir(paths.get_cache_path('md5sums')):
            # Remove only files in the same language and matching the solution regex
            if package_util.get_file_lang(solution) == lang and \
                    solutions_re.match(solution) is not None:
                os.unlink(paths.get_cache_path('md5sums', solution))

    info.md5sum = md5sum
    info.save(file_path)


def process_extra_compilation_files(extra_compilation_files, task_id):
    """
    Checks if extra compilation files have changed and saves them to cache.
    If they have, removes all cached solutions that use them.
    :param extra_compilation_files: List of extra compilation files
    :param task_id: Task id
    """
    for file in extra_compilation_files:
        file_path = os.path.join(os.getcwd(), "prog", file)
        if not os.path.exists(file_path):
            continue
        md5sum = util.get_file_md5(file_path)
        lang = package_util.get_file_lang(file)
        if lang == 'h':
            lang = 'cpp'
        _check_file_changed(file_path, lang, task_id)


def process_extra_execution_files(extra_execution_files, task_id):
    """
    Checks if extra execution files have changed and saves them to cache.
    If they have, removes all cached solutions that use them.
    :param extra_execution_files: List of extra execution files
    :param task_id: Task id
    """
    for lang, files in extra_execution_files.items():
        for file in files:
            file_path = os.path.join(os.getcwd(), "prog", file)
            if not os.path.exists(file_path):
                continue
            _check_file_changed(file_path, lang, task_id)


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
        with open(paths.get_cache_path("test"), "w") as f:
            f.write("test")
        os.unlink(paths.get_cache_path("test"))
    except PermissionError:
        util.exit_with_error("You don't have permission to access the `.cache/` directory. "
                             "`sinol-make` needs to be able to write to this directory.")


def has_file_changed(file_path: str) -> bool:
    """
    Checks if file has changed since last compilation.
    :param file_path: Path to the file
    :return: True if file has changed, False otherwise
    """
    try:
        info = get_cache_file(file_path)
        return info.md5sum != util.get_file_md5(file_path)
    except FileNotFoundError:
        return True


def check_correct_solution(task_id: str):
    """
    Checks if correct solution has changed. If it did, removes cache for input files.
    :param task_id: Task id
    """
    try:
        solution = package_util.get_correct_solution(task_id)
    except FileNotFoundError:
        return

    if has_file_changed(solution) and os.path.exists(os.path.join(os.getcwd(), 'in', '.md5sums')):
        os.unlink(os.path.join(os.getcwd(), 'in', '.md5sums'))


def create_cache_dirs():
    """
    Creates all required cache directories.
    """
    for dir in [
        paths.get_cache_path(),
        paths.get_executables_path(),
        paths.get_compilation_log_path(),
        paths.get_executions_path(),
        paths.get_chkwer_path(),
        paths.get_cache_path('md5sums'),
        paths.get_cache_path('doc_logs'),
    ]:
        os.makedirs(dir, exist_ok=True)
