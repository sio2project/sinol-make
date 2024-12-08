from typing import List
import sys
import glob
import yaml
import os
import pytest
import fnmatch
import multiprocessing as mp

from sinol_make import sio2jail, util
from sinol_make.helpers import compile, paths, cache, oicompare
from sinol_make.interfaces.Errors import CompilationError


def _compile(args):
    package, file_path = args
    os.chdir(package)
    output = paths.get_executables_path(os.path.splitext(os.path.basename(file_path))[0] + ".e")
    compile_log_path = paths.get_compilation_log_path(os.path.basename(file_path) + ".compile_log")
    basename = os.path.basename(file_path)
    use_fsanitize = fnmatch.fnmatch(basename, "*ingen*") or fnmatch.fnmatch(basename, "*inwer*")
    try:
        with open(compile_log_path, "w") as compile_log:
            compile.compile(file_path, output, compile_log=compile_log, use_fsanitize=use_fsanitize)
    except CompilationError:
        compile.print_compile_log(compile_log_path)
        raise


def pytest_addoption(parser):
    parser.addoption("--github-runner", action="store_true", help="if set, will run tests specified for GitHub runner")
    parser.addoption(
        '--time-tool',
        choices=['sio2jail', 'time'],
        action='append',
        default=[],
        help='Time tool to use. Default: if linux - both, otherwise time'
    )
    parser.addoption("--no-precompile", action="store_true", help="if set, will not precompile all solutions")
    parser.addoption("--cpus", type=int, help="number of cpus to use, by default all available",
                     default=util.default_cpu_count())


def pytest_configure(config):
    packages = glob.glob(os.path.join(os.path.dirname(__file__), "packages", "*"))
    if not config.getoption("--no-precompile"):
        print("Collecting solutions...")

        files_to_compile = []
        for package in packages:
            cwd = os.getcwd()
            os.chdir(package)
            cache.create_cache_dirs()
            os.chdir(cwd)

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

    oicompare.check_and_download()


def pytest_generate_tests(metafunc):
    if "time_tool" in metafunc.fixturenames:
        time_tools = []
        if metafunc.config.getoption("time_tool") != []:
            time_tools = metafunc.config.getoption("time_tool")
        elif sio2jail.sio2jail_supported():
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
        if "sio2jail" in item.keywords:
            if not sio2jail.sio2jail_supported() or config.getoption("--time-tool") == ["time"] or \
                    config.getoption("--github-runner"):
                item.add_marker(pytest.mark.skip(reason="sio2jail required"))
