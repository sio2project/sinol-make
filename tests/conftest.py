from typing import List
import sys
import glob
import yaml
import os
import pytest
import fnmatch
import multiprocessing as mp

from sinol_make import util
from sinol_make.compilers.CompilersManager import CompilerManager
from sinol_make.helpers import paths, package_util
from sinol_make.interfaces.Errors import CompilationError
from sinol_make.programs.checker import Checker
from sinol_make.programs.ingen import Ingen
from sinol_make.programs.inwer import Inwer
from sinol_make.programs.solution import Solution
from sinol_make.timetools.TimeToolManager import TimeToolManager
from sinol_make.executor import Executor


def _compile(args):
    package, program = args
    os.chdir(package)
    exe, compile_log = program.compile()
    if exe is None:
        CompilerManager.print_compile_log(compile_log)
        raise CompilationError(f"Compilation failed for {program.basename}")


def pytest_addoption(parser):
    parser.addoption("--github-runner", action="store_true", help="if set, will run tests specified for GitHub runner")
    parser.addoption(
        '--time-tool',
        choices=['sio2jail', 'time'],
        action='append',
        default=[],
        help='Time tool to use. Default: oiejq'
    )
    parser.addoption("--no-precompile", action="store_true", help="if set, will not precompile all solutions")
    parser.addoption("--cpus", type=int, help="number of cpus to use, by default all available",
                     default=util.default_cpu_count())


def pytest_configure(config):
    packages = glob.glob(os.path.join(os.path.dirname(__file__), "packages", "*"))
    if not config.getoption("--no-precompile"):
        print("Collecting solutions...")

        timetool_manager = TimeToolManager()
        executor = Executor(timetool_manager)
        compiler_manager = CompilerManager(None)

        files_to_compile = []
        for package in packages:
            if os.path.exists(os.path.join(package, "no-precompile")):
                print(f'Skipping precompilation for {package} due to no-precompile file')
                continue

            for d in ["compilation", "executables"]:
                os.makedirs(os.path.join(package, ".cache", d), exist_ok=True)

            cwd = os.getcwd()
            os.chdir(package)
            task_id = package_util.get_task_id(False)
            for program in glob.glob(os.path.join(package, "prog", "*")):
                for cls in [Solution, Ingen, Inwer, Checker]:
                    try:
                        prog = cls(executor, compiler_manager, task_id, program)
                        files_to_compile.append((package, prog))
                    except FileNotFoundError:
                        pass
            os.chdir(cwd)

        print("Precompiling solutions...")
        with mp.Pool(config.getoption("--cpus")) as pool:
            for i, _ in enumerate(pool.imap(_compile, files_to_compile)):
                print(f"Precompiled {i + 1}/{len(files_to_compile)} solutions", end="\r")
        print("\nPrecompilation finished")
    else:
        print("Skipping precompilation")

    # We remove tests cache as it may interfere with testing.
    for package in packages:
        for md5sum_file in glob.glob(os.path.join(package, ".cache", "md5sums", "*")):
            try:
                with open(md5sum_file, "r") as f:
                    data = yaml.load(f, Loader=yaml.FullLoader)

                try:
                    if "tests" in data and data["tests"] != {}:
                        print(f"Removing tests cache for `{os.path.basename(md5sum_file)}`")
                        data["tests"] = {}
                        with open(md5sum_file, "w") as f:
                            yaml.dump(data, f)
                except TypeError:
                    # Cache file is probably old/broken, we can delete it.
                    os.unlink(md5sum_file)
            except FileNotFoundError:
                pass


def pytest_generate_tests(metafunc):
    if "time_tool" in metafunc.fixturenames:
        time_tools = []
        if metafunc.config.getoption("time_tool") != []:
            time_tools = metafunc.config.getoption("time_tool")
        elif util.is_linux():
            time_tools = ["sio2jail", "time"]
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
