import os
import glob
import subprocess

from sinol_make.helpers import compile



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


def get_weak_compilation_flags_package_path():
    """
    Get path to package for testing weak compilation flags (/test/packages/wcf)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "wcf")


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

def create_ins(package_path):
    """
    Create .in files for package.
    """
    ingen = glob.glob(os.path.join(package_path, "prog", "*ingen.*"))[0]
    ingen_executable = os.path.join(package_path, "cache", "executables", "ingen.e")
    os.makedirs(os.path.join(package_path, "cache", "executables"), exist_ok=True)
    assert compile.compile(ingen, ingen_executable)
    os.chdir(os.path.join(package_path, "in"))
    os.system("../cache/executables/ingen.e")
    os.chdir(package_path)


def create_outs(package_path):
    """
    Create .out files for package.
    """
    solution = glob.glob(os.path.join(package_path, "prog", "???.*"))[0]
    solution_executable = os.path.join(package_path, "cache", "executables", "solution.e")
    os.makedirs(os.path.join(package_path, "cache", "executables"), exist_ok=True)
    assert compile.compile(solution, solution_executable)
    os.chdir(os.path.join(package_path, "in"))
    for file in glob.glob("*.in"):
        with open(file, "r") as in_file, open(os.path.join("../out", file.replace(".in", ".out")), "w") as out_file:
            subprocess.Popen([os.path.join(package_path, "cache", "executables", "solution.e")],
                             stdin=in_file, stdout=out_file).wait()
    os.chdir(package_path)


def create_ins_outs(package_path):
    """
    Create .in and .out files for package.
    """
    create_ins(package_path)
    has_lib = len(glob.glob(os.path.join(package_path, "prog", "???lib.*"))) > 0
    if not has_lib:
        create_outs(package_path)
