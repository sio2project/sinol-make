import sys
from io import StringIO

from sinol_make import util
from sinol_make.commands.inwer.inwer_util import sort_tests
from sinol_make.structs.chkwer_structs import TableData


def print_view(term_width, term_height, table_data: TableData):
    """
    Prints current results of test verification.
    """

    previous_stdout = sys.stdout
    new_stdout = StringIO()
    sys.stdout = new_stdout

    results = table_data.results
    column_lengths = [0, len('Points') + 1, 0]
    tests = []
    for result in results.values():
        column_lengths[0] = max(column_lengths[0], len(result.test_name))
        tests.append(result.test_path)
    tests = sort_tests(tests, table_data.task_id)

    # 6 is for " | " between columns, 3 for margin.
    column_lengths[2] = max(10, term_width - column_lengths[0] - column_lengths[1] - 6 - 3)
    margin = "  "

    def print_line_separator():
        res = "-" * (column_lengths[0] + 3) + "+" + "-" * (column_lengths[1] + 1) + "+"
        res += "-" * (term_width - len(res) - 1)
        print(res)

    print_line_separator()

    print(margin + "Test".ljust(column_lengths[0]) + " | " + "Points" + " | " + "Comment")
    print_line_separator()

    last_group = None
    for test_path in tests:
        result = results[test_path]
        if last_group is not None and last_group != result.test_group:
            print_line_separator()
        last_group = result.test_group
        print(margin + result.test_name.ljust(column_lengths[0]) + " | ", end='')

        if result.run:
            if result.ok:
                if result.points == table_data.max_score:
                    print(util.info(str(result.points).ljust(column_lengths[1] - 1)), end='')
                else:
                    print(util.warning(str(result.points).ljust(column_lengths[1] - 1)), end='')
            else:
                print(util.error(str(result.points).ljust(column_lengths[1] - 1)), end='')
        else:
            print(util.warning("...".ljust(column_lengths[1] - 1)), end='')
        print(" | ", end='')

        output = []
        if result.run:
            if result.comment:
                print(result.comment)
            else:
                print(util.color_gray("No comment"))

    print_line_separator()
    print()
    print()

    sys.stdout = previous_stdout
    return new_stdout.getvalue().splitlines(), None, "Use arrows to move."
