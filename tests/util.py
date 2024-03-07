import os
import glob
import subprocess

from sinol_make.helpers import compile, paths, package_util


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


def create_ins(package_path, task_id):
    """
    Create .in files for package.
    """
    all_ingens = package_util.get_files_matching_pattern(task_id, f'{task_id}ingen.*')
    if len(all_ingens) == 0:
        return
    ingen = all_ingens[0]
    ingen_executable = paths.get_executables_path("ingen.e")
    os.makedirs(paths.get_executables_path(), exist_ok=True)
    assert compile.compile(ingen, ingen_executable)
    os.chdir(os.path.join(package_path, "in"))
    os.system("../.cache/executables/ingen.e")
    os.chdir(package_path)


def create_outs(package_path, task_id):
    """
    Create .out files for package.
    """
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


def create_ins_outs(package_path):
    """
    Create .in and .out files for package.
    """
    os.chdir(package_path)
    task_id = package_util.get_task_id()
    create_ins(package_path, task_id)
    has_lib = package_util.any_files_matching_pattern(task_id, f"{task_id}lib.*")
    if not has_lib:
        create_outs(package_path, task_id)
