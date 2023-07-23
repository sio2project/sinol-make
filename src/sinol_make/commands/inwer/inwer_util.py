import glob
import os
import sys
from io import StringIO
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


def compile_inwer(inwer_path: str, args: argparse.Namespace, weak_compilation_flags=False):
    """
    Compiles inwer and returns path to compiled executable and path to compile log.
    """
    compilers = compiler.verify_compilers(args, [inwer_path])
    return compile.compile_file(inwer_path, package_util.get_executable(inwer_path), compilers, weak_compilation_flags)


def print_view(term_width, term_height, table_data: TableData):
    """
    Prints current results of test verification.
    """

    previous_stdout = sys.stdout
    new_stdout = StringIO()
    sys.stdout = new_stdout

    results = table_data.results
    column_lengths = [0, len('Group') + 1, len('Status') + 1, 0]
    sorted_test_paths = []
    for result in results.values():
        column_lengths[0] = max(column_lengths[0], len(result.test_name))
        column_lengths[1] = max(column_lengths[1], len(result.test_group))
        sorted_test_paths.append(result.test_path)
    sorted_test_paths.sort()

    column_lengths[3] = max(10, term_width - column_lengths[0] - column_lengths[1] - column_lengths[2] - 9 - 3) # 9 is for " | " between columns, 3 for margin.
    margin = "  "

    def print_line_separator():
        res = "-" * (column_lengths[0] + 3) + "+" + "-" * (column_lengths[1] + 1) + "+" + "-" * (column_lengths[2] + 1) + "+"
        res += "-" * (term_width - len(res) - 1)
        print(res)

    print_line_separator()

    print(margin + "Test".ljust(column_lengths[0]) + " | " + "Group".ljust(column_lengths[1] - 1) + " | " + "Status" +
          " | " + "Output")
    print_line_separator()

    for test_path in sorted_test_paths:
        result = results[test_path]
        print(margin + result.test_name.ljust(column_lengths[0]) + " | ", end='')
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
        output.pop(0)

        for line in output:
            print(" " * (column_lengths[0] + 2) + " | " + " " * (column_lengths[1] - 1) + " | " +
                  " " * (column_lengths[2] - 1) + " | " + line.ljust(column_lengths[3]))

    print_line_separator()
    print()
    print()

    sys.stdout = previous_stdout
    return new_stdout.getvalue().splitlines(), None, "Use arrows to move."
