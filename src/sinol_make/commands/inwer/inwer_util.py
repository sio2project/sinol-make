import glob
import os
import sys

import argparse

from sinol_make import util
from sinol_make.commands.inwer import TestResult, TableData
from sinol_make.helpers import compile, package_util
from sinol_make.helpers import compiler
from sinol_make.interfaces.Errors import CompilationError


def get_inwer_path(task_id: str, path = None) -> str or None:
    """
    Returns path to inwer executable for given task or None if no inwer was found.
    """
    if path is None:
        inwers = glob.glob(os.path.join(os.getcwd(), 'prog', f'{task_id}inwer.*'))
        if len(inwers) == 0:
            return None
        return inwers[0]
    else:
        inwer = os.path.join(os.getcwd(), path)
        if os.path.exists(inwer):
            return inwer
        return None


def compile_inwer(inwer_path: str, args: argparse.Namespace):
    """
    Compiles inwer and returns path to compiled executable and path to compile log.
    """
    compilers = compiler.verify_compilers(args, [inwer_path])
    return compile.compile_file(inwer_path, package_util.get_executable(inwer_path), compilers)


def print_view(table_data: TableData):
    """
    Prints current results of test verification.
    """

    sys.stdout.write(f'\033[{table_data.previous_vertical_height}A')
    table_data.previous_vertical_height = 2

    results = table_data.results
    column_lengths = [0, len('Group') + 1, len('Status') + 1, 0]
    sorted_test_paths = []
    for result in results.values():
        column_lengths[0] = max(column_lengths[0], len(result.test_name) + 1)
        column_lengths[1] = max(column_lengths[1], len(result.test_group) + 1)
        sorted_test_paths.append(result.test_path)
    sorted_test_paths.sort()

    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = 80

    column_lengths[3] = max(10, terminal_width - 20 - column_lengths[0] - column_lengths[1] - column_lengths[2] - 9) # 9 is for " | " between columns

    print("Test".ljust(column_lengths[0]) + " | " + "Group".ljust(column_lengths[1] - 1) + " | " + "Status" + " | " + "Output".ljust(column_lengths[3]))
    print("-" * (column_lengths[0] + 1) + "+" + "-" * (column_lengths[1] + 1) + "+" +
          "-" * (column_lengths[2] + 1) + "+" + "-" * (column_lengths[3] + 1))

    for test_path in sorted_test_paths:
        result = results[test_path]
        print(result.test_name.ljust(column_lengths[0]) + " | ", end='')
        print(result.test_group.ljust(column_lengths[1] - 1) + " | ", end='')

        if result.verified:
            if result.valid:
                print(util.info("OK".ljust(column_lengths[2] - 1)), end='')
            else:
                print(util.error("ERROR".ljust(column_lengths[2] - 1)), end='')
        else:
            print(util.warning("...".ljust(column_lengths[2] - 1)), end='')
        print(" | ", end='')

        output = []
        if result.verified:
            split_output = result.output.split('\n')
            for line in split_output:
                output += [line[i:i + column_lengths[3]] for i in range(0, len(line), column_lengths[3])]
        else:
            output.append("")

        print(output[0].ljust(column_lengths[3]))
        table_data.previous_vertical_height += 1
        output.pop(0)

        for line in output:
            print(" " * (column_lengths[0]) + " | " + " " * (column_lengths[1] - 1) + " | " +
                  " " * (column_lengths[2] - 1) + " | " + line.ljust(column_lengths[3]))
            table_data.previous_vertical_height += 1
