import os
import glob

from sinol_make.helpers import compile


def get_simple_package_path():
    """Get path to simple package (/tests/packages/abc)"""
    return os.path.join(os.path.dirname(__file__), "packages", "abc")


def get_verify_status_package_path():
    """
    Get path to package for veryfing status order (/test/packages/vso)
    """
    return os.path.join(os.path.dirname(__file__), "packages", "vso")


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
        os.system(f'{os.path.join(package_path, "cache", "executables", "solution.e")} < {file} > ../out/{file.replace(".in", ".out")}')
    os.chdir(package_path)


def create_ins_outs(package_path):
    """
    Create .in and .out files for package.
    """
    create_ins(package_path)
    create_outs(package_path)
