import os
import glob
import hashlib
import shutil
import subprocess
import tempfile

from sinol_make.helpers import compile, paths, package_util

# Name of the environment variable holding the directory in which tests generated for packages
# are kept. It is set by `tests/conftest.py` for the whole pytest session.
GENERATED_TESTS_DIR_ENV = "SINOL_MAKE_GENERATED_TESTS_DIR"


def get_simple_package_path():
    """Get path to simple package (/tests/packages/abc)"""
    return os.path.join(os.path.dirname(__file__), "packages", "abc")


def get_verify_status_package_path():
    """
    Get path to package for veryfing status order (/test/packages/vso)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "vso")


def get_checker_package_path():
    """
    Get path to package for checker (/test/packages/chk)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "chk")


def get_library_package_path():
    """
    Get path to package with library command (/test/packages/lib)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "lib")


def get_library_string_args_package_path():
    """
    Get path to package with library command with string extra_compilation_args (/test/packages/lsa)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "lsa")


def get_weak_compilation_flags_package_path():
    """
    Get path to package for testing weak compilation flags (/test/packages/wcf)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "wcf")


def get_oioioi_compilation_flags_package_path():
    """
    Get path to package for testing oioioi compilation flags (/test/packages/oioioi_flags)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "oioioi_flags")


def get_inwer_package_path():
    """
    Get path to package for inwer command (/test/packages/wer)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "wer")


def get_shell_ingen_pack_path():
    """
    Get path to package for testing shell ingen (/test/packages/gen)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "gen")


def get_limits_package_path():
    """
    Get path to package with `time_limits` and `memory_limits` present in config (/test/packages/lim)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "lim")


def get_handwritten_package_path():
    """
    Get path to package with handwritten tests (/test/packages/hw)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "hwr")


def get_stack_size_package_path():
    """
    Get path to package for testing of changing stack size (/test/packages/stc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "stc")


def get_override_limits_package_path():
    """
    Get path to package with `override_limits` present in config (/test/packages/ovl)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "ovl")


def get_doc_package_path():
    """
    Get path to package for testing `doc` command (/test/packages/doc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "doc")


def get_ps_doc_package_path():
    """
    Get path to package for testing `doc` command (version with ps images) (/test/packages/ps_doc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "ps_doc")


def get_luadoc_package_path():
    """
    Get path to package for testing `doc` command (version that requests lualatex in config.yml) (/test/packages/luadoc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "luadoc")


def get_long_name_package_path():
    """
    Get path to package with long name (/test/packages/long_package_name)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "long_package_name")


def get_undocumented_options_package_path():
    """
    Get path to package with undocumented options in config.yml (/test/packages/undoc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "undocumented_options")


def get_example_tests_package_path():
    """
    Get path to package with only example tests (/tests/packages/example_tests)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "example_tests")


def get_icpc_package_path():
    """
    Get path to package with icpc contest type (/tests/packages/icpc)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "icpc")


def get_long_solution_names_package():
    """
    Get path to package with long solution names (/tests/packages/long_solution_names)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "long_solution_names")


def get_large_output_package_path():
    """
    Get path to package with large output (/tests/packages/large_output)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "large_output")


def get_rust_package_path():
    """Get path to Rust test package (/tests/packages/rus)"""
    return os.path.join(os.path.dirname(__file__), "packages", "rus")


def get_ocen_package_path():
    """
    Get path to package for testing ocen archive creation (/tests/packages/ocen)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "ocen")


def get_bad_tests_package_path():
    """
    Get path to package with bad tests (/tests/packages/bad_tests)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "bad_tests")


def get_dlazaw_package():
    """
    Get path to package with dlazaw dir and no ocen tests (/tests/packages/dlazaw)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "dlazaw")


def get_stresstest_package_path():
    """
    Get path to package with stresstest.sh (/tests/packages/stresstest)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "stresstest")


def get_dependencies_package_path():
    """
    Get path to package with subtask dependencies (/tests/packages/dep)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "dep")


def get_simple_interactive_package():
    """
    Get path to package with simple interactive task (/tests/packages/simple_interactive)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "simple_interactive")


def get_static_tests_package_path():
    """
    Get path to package with static tests (/tests/packages/static_tests)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "static_tests")


def get_two_interactive_package():
    """
    Get path to interactive package with two processes (/tests/packages/two_interactive)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "two_interactive")

def get_score_package():
    """
    Get path to package with custom sinol_total_score (/tests/packages/score)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "score")

def _get_generated_tests_dir():
    """
    Get path to the directory in which tests generated for packages are kept.
    """
    path = os.environ.get(GENERATED_TESTS_DIR_ENV,
                          os.path.join(tempfile.gettempdir(), "sinol-make-generated-tests"))
    os.makedirs(path, exist_ok=True)
    return path


def _package_hash(package_path, *extra_globs):
    """
    Calculate a hash of everything in the package which can change the generated tests.
    """
    md5 = hashlib.md5()
    files = glob.glob(os.path.join(package_path, "prog", "**"), recursive=True)
    for pattern in extra_globs:
        files += glob.glob(os.path.join(package_path, pattern))
    for file in sorted(files):
        if not os.path.isfile(file):
            continue
        md5.update(os.path.relpath(file, package_path).encode())
        with open(file, "rb") as f:
            md5.update(f.read())
    return md5.hexdigest()


def _restore_generated(key, directory):
    """
    Copy tests generated previously for `key` into `directory`.
    :return: False if nothing was generated for `key` yet, True otherwise.
    """
    generated = os.path.join(_get_generated_tests_dir(), key)
    if not os.path.exists(generated):
        return False
    shutil.copytree(generated, directory, dirs_exist_ok=True)
    return True


def _save_generated(key, directory):
    """
    Save tests generated in `directory`, so that other tests using the same package can reuse them.
    """
    generated_tests_dir = _get_generated_tests_dir()
    tmpdir = tempfile.mkdtemp(dir=generated_tests_dir)
    try:
        copied = os.path.join(tmpdir, "tests")
        shutil.copytree(directory, copied)
        try:
            os.rename(copied, os.path.join(generated_tests_dir, key))
        except OSError:
            # Another process saved the same tests first, which is fine.
            pass
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def create_ins(package_path, task_id):
    """
    Create .in files for package.
    """
    all_ingens = package_util.get_files_matching_pattern(task_id, f'{task_id}ingen.*')
    if len(all_ingens) == 0:
        return
    ingen = all_ingens[0]
    in_dir = os.path.join(package_path, "in")
    key = f'{task_id}-in-{_package_hash(package_path, os.path.join("in", "*"))}'
    if _restore_generated(key, in_dir):
        return

    ingen_executable = paths.get_executables_path("ingen.e")
    os.makedirs(paths.get_executables_path(), exist_ok=True)
    # `sinol-make` compiles ingens with this flag, so it is used here as well to reuse the executable
    # compiled when the tests were started.
    assert compile.compile(ingen, ingen_executable, extra_compilation_args=['-D_INGEN'])
    os.chdir(in_dir)
    os.system("../.cache/executables/ingen.e")
    os.chdir(package_path)
    _save_generated(key, in_dir)


def create_outs(package_path, task_id):
    """
    Create .out files for package.
    """
    out_dir = os.path.join(package_path, "out")
    key = f'{task_id}-out-{_package_hash(package_path, os.path.join("in", "*"))}'
    if _restore_generated(key, out_dir):
        return

    solution = package_util.get_files_matching_pattern(task_id, f'{task_id}.*')[0]
    solution_executable = paths.get_executables_path("solution.e")
    os.makedirs(paths.get_executables_path(), exist_ok=True)
    assert compile.compile(solution, solution_executable)
    os.chdir(os.path.join(package_path, "in"))
    for file in glob.glob("*.in"):
        with open(file, "r") as in_file, open(os.path.join("../out", file.replace(".in", ".out")), "w") as out_file:
            subprocess.Popen([os.path.join(package_path, ".cache", "executables", "solution.e")],
                             stdin=in_file, stdout=out_file).wait()
    os.chdir(package_path)
    _save_generated(key, out_dir)


def create_ins_outs(package_path):
    """
    Create .in and .out files for package.
    """
    os.chdir(package_path)
    task_id = package_util.get_task_id()
    task_type = package_util.get_task_type_cls()
    create_ins(package_path, task_id)
    has_lib = package_util.any_files_matching_pattern(task_id, f"{task_id}lib.*")
    if not has_lib and task_type.run_outgen():
        create_outs(package_path, task_id)
