import multiprocessing as mp
import argparse
import os

from sinol_make.contest_types import get_contest_type
from sinol_make.commands.run import Command
from tests import util


def get_command(path = None):
    """
    Helper to get a command object with the constants set.
    """
    if path is None:
        path = util.get_simple_package_path()
    os.chdir(path)
    command: Command = util.get_run_command()
    command.base_run(argparse.Namespace(
        hide_memory=False,
        weak_compilation_flags=False,
    ))
    command.cpus = mp.cpu_count()
    command.checker = None
    command.failed_compilations = []
    command.contest = get_contest_type()
    return command
