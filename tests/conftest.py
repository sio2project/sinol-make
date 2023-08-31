from typing import List
import sys
import glob
import os
import pytest
import multiprocessing as mp

from sinol_make.helpers import compile


def _compile(args):
    package, file_path = args
    os.chdir(package)
    output = os.path.join(package, ".cache", "executables", os.path.splitext(os.path.basename(file_path))[0] + ".e")
    with open(os.path.join(package, ".cache", "compilation",
                           os.path.basename(file_path) + ".compile_log"), "w") as compile_log:
        compile.compile(file_path, output, compile_log=compile_log)


def pytest_addoption(parser):
    parser.addoption("--github-runner", action="store_true", help="if set, will run tests specified for GitHub runner")
    parser.addoption(
        '--time-tool',
        choices=['oiejq', 'time'],
        action='append',
        default=[],
        help='Time tool to use. Default: oiejq'
    )
    parser.addoption("--no-precompile", action="store_true", help="if set, will not precompile all solutions")
    parser.addoption("--cpus", type=int, help="number of cpus to use, by default all available",
                     default=mp.cpu_count())


def pytest_configure(config):
    if not config.getoption("--no-precompile"):
        print("Collecting solutions...")

        files_to_compile = []
        packages = glob.glob(os.path.join(os.path.dirname(__file__), "packages", "*"))
        for package in packages:
            if os.path.exists(os.path.join(package, "no-precompile")):
                print(f'Skipping precompilation for {package} due to no-precompile file')
                continue

            for d in ["compilation", "executables"]:
                os.makedirs(os.path.join(package, ".cache", d), exist_ok=True)

            for program in glob.glob(os.path.join(package, "prog", "*")):
                if os.path.isfile(program) and os.path.splitext(program)[1] in [".c", ".cpp", ".py", ".java"]:
                    files_to_compile.append((package, program))

        print("Precompiling solutions...")
        with mp.Pool(config.getoption("--cpus")) as pool:
            for i, _ in enumerate(pool.imap(_compile, files_to_compile)):
                print(f"Precompiled {i + 1}/{len(files_to_compile)} solutions", end="\r")
    else:
        print("Skipping precompilation")


def pytest_generate_tests(metafunc):
    if "time_tool" in metafunc.fixturenames:
        time_tools = []
        if metafunc.config.getoption("time_tool") != []:
            time_tools = metafunc.config.getoption("time_tool")
        elif sys.platform == "linux":
            time_tools = ["oiejq", "time"]
        else:
            time_tools = ["time"]
        metafunc.parametrize("time_tool", time_tools)


def pytest_collection_modifyitems(config, items: List[pytest.Item]):
    if config.getoption("--github-runner"):
        for item in items:
            if "github_runner" not in item.keywords:
                item.add_marker(pytest.mark.skip(reason="not for GitHub runner"))
    else:
        for item in items:
            if "github_runner" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="only for GitHub runner"))

    for item in items:
        if "oiejq" in item.keywords:
            if sys.platform != "linux" or config.getoption("--time-tool") == ["time"] or \
                    config.getoption("--github-runner"):
                item.add_marker(pytest.mark.skip(reason="oiejq required"))
