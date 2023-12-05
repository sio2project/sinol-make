from typing import List
from io import StringIO
import sys
import collections

from sinol_make import util
from sinol_make.helpers import package_util
from sinol_make.programs.solution import Solution
from sinol_make.structs.run_structs import RunExecution, PrintData
from sinol_make.structs.status_structs import Status
from sinol_make.tests.input import InputTest


def color_memory(memory, limit):
    if memory == -1: return util.color_yellow("")
    memory_str = "%.1fMB" % (memory / 1024.0)
    if memory > limit:
        return util.color_red(memory_str)
    elif memory > limit / 2.0:
        return util.color_yellow(memory_str)
    else:
        return util.color_green(memory_str)


def color_time(time, limit):
    if time == -1: return util.color_yellow("")
    time_str = "%.2fs" % (time / 1000.0)
    if time >= limit:
        return util.color_red(time_str)
    elif time > limit / 2.0:
        return util.color_yellow(time_str)
    else:
        return util.color_green(time_str)


def colorize_status(status):
    if status == Status.OK: return util.bold(util.color_green(status))
    if status == Status.PENDING: return util.warning(status)
    return util.error(status)


def update_group_status(group_status, new_status):
    order = [Status.CE, Status.RV, Status.TL, Status.ML, Status.RE, Status.WA, Status.OK, Status.PENDING]
    if order.index(new_status) < order.index(group_status):
        return new_status
    return group_status


def print_view(term_width, term_height, task_id, program_groups_scores, all_results, print_data: PrintData,
               solutions: List[Solution], executions: List[RunExecution], groups, scores, tests: List[InputTest],
               possible_score, cpus, hide_memory, config, contest, args):
    width = term_width - 11  # First column has 6 characters, the " | " separator has 3 characters and 2 for margin
    # First column has 11 characters and each solution has 13 characters and the " | " separator has 3 characters
    programs_in_row = width // 16
    if programs_in_row == 0:
        return ["Terminal window is too small to display the results."], None, None

    previous_stdout = sys.stdout
    output = StringIO()
    sys.stdout = output

    program_scores = collections.defaultdict(int)
    # program_times and program_memory are dictionaries of tuples (max, limit),
    # where max is the maximum time/memory used by a program and
    # limit is the time/memory limit of the test that caused the maximum
    # time/memory usage.
    program_times = collections.defaultdict(lambda: (-1, 0))
    program_memory = collections.defaultdict(lambda: (-1, 0))

    time_sum = 0
    for solution in solutions:
        lang = solution.lang
        for test in tests:
            time_sum += package_util.get_time_limit(test, config, lang, task_id, args)

    time_remaining = (len(executions) - print_data.i - 1) * 2 * time_sum / cpus / 1000.0
    title = 'Done %4d/%4d. Time remaining (in the worst case): %5d seconds.' \
            % (print_data.i + 1, len(executions), time_remaining)
    title = title.center(term_width)
    margin = "  "
    for program_ix in range(0, len(solutions), programs_in_row):
        program_group = solutions[program_ix:program_ix + programs_in_row]

        def print_table_end():
            print("-" * 8, end="-+-")
            for i in range(len(program_group)):
                if i != len(program_group) - 1:
                    print("-" * 13, end="-+-")
                else:
                    print("-" * 13, end="-+")
            print()

        print_table_end()

        print(margin + "groups", end=" | ")
        next_row = {solution: solution.basename for solution in program_group}
        first = True
        while next_row != {}:
            if first:
                first = False
            else:
                print(margin + " " * 6, end=" | ")

            for solution in program_group:
                if solution in next_row:
                    to_print = next_row[solution]
                    if len(to_print) > 13:
                        print(to_print[:13], end=" | ")
                        next_row[solution] = to_print[13:]
                    else:
                        print(to_print.ljust(13), end=" | ")
                        del next_row[solution]
                else:
                    print(" " * 13, end=" | ")
            print()

        print(8 * "-", end=" | ")
        for program in program_group:
            print(13 * "-", end=" | ")
        print()
        for group in groups:
            print(margin + "%6s" % group, end=" | ")
            for program in program_group:
                lang = program.lang
                results = all_results[program.basename][group]
                group_status = Status.OK
                test_scores = []
                any_pending = False

                for test in results:
                    test_scores.append(results[test].Points)
                    status = results[test].Status
                    if status == Status.PENDING:
                        any_pending = True

                    if results[test].Time is not None:
                        if program_times[program.basename][0] < results[test].Time:
                            program_times[program.basename] = (
                                results[test].Time,
                                package_util.get_time_limit(test, config, lang, task_id, args)
                            )
                    elif status == Status.TL:
                        program_times[program.basename] = (
                            2 * package_util.get_time_limit(test, config, lang, task_id, args),
                            package_util.get_time_limit(test, config, lang, task_id, args)
                        )
                    if results[test].Memory is not None:
                        if program_memory[program.basename][0] < results[test].Memory:
                            program_memory[program.basename] = (
                                results[test].Memory,
                                package_util.get_memory_limit(test, config, lang, task_id, args)
                            )
                    elif status == Status.ML:
                        program_memory[program.basename] = (
                            2 * package_util.get_memory_limit(test, config, lang, task_id, args),
                            package_util.get_memory_limit(test, config, lang, task_id, args)
                        )
                    if status == Status.PENDING:
                        group_status = Status.PENDING
                    else:
                        group_status = update_group_status(group_status, status)

                points = contest.get_group_score(test_scores, scores[group])
                if any_pending:
                    print(" " * 6 + ("?" * len(str(scores[group]))).rjust(3) +
                          f'/{str(scores[group]).rjust(3)}', end=' | ')
                else:
                    if group_status == Status.OK:
                        status_text = util.bold(util.color_green(group_status.ljust(6)))
                    else:
                        status_text = util.bold(util.color_red(group_status.ljust(6)))
                    print(f"{status_text}{str(points).rjust(3)}/{str(scores[group]).rjust(3)}", end=' | ')
                program_groups_scores[program.basename][group] = {"status": group_status, "points": points}
            print()
        for program in program_group:
            program_scores[program.basename] = contest.get_global_score(program_groups_scores[program.basename],
                                                                        possible_score)

        print(8 * " ", end=" | ")
        for program in program_group:
            print(13 * " ", end=" | ")
        print()
        print(margin + "points", end=" | ")
        for program in program_group:
            print(util.bold("      %3s/%3s" % (program_scores[program.basename], possible_score)), end=" | ")
        print()
        print(margin + "  time", end=" | ")
        for program in program_group:
            program_time = program_times[program.basename]
            print(util.bold(("%23s" % color_time(program_time[0], program_time[1]))
                            if 2 * program_time[1] > program_time[0] >= 0
                            else "      " + 7 * '-'), end=" | ")
        print()
        print(margin + "memory", end=" | ")
        for program in program_group:
            program_mem = program_memory[program]
            print(util.bold(("%23s" % color_memory(program_mem[0], program_mem[1]))
                            if 2 * program_mem[1] > program_mem[0] >= 0
                            else "      " + 7 * '-'), end=" | ")
        print()
        print(8 * " ", end=" | ")
        for program in program_group:
            print(13 * " ", end=" | ")
        print()

        def print_group_seperator():
            print(8 * "-", end=" | ")
            for program in program_group:
                print(13 * "-", end=" | ")
            print()

        print_group_seperator()

        last_group = None
        for test in tests:
            group = test.group
            if last_group != group:
                if last_group is not None:
                    print_group_seperator()
                last_group = group

            print(margin + "%6s" % test.test_id, end=" | ")
            for program in program_group:
                lang = program.lang
                result = all_results[program.basename][group][test]
                status = result.Status
                if status == Status.PENDING:
                    print(13 * ' ', end=" | ")
                else:
                    print("%3s" % colorize_status(status),
                          ("%20s" % color_time(result.Time,
                                               package_util.get_time_limit(test, config, lang, task_id, args)))
                          if result.Time is not None else 10 * " ", end=" | ")
            print()
            if not hide_memory:
                print(8 * " ", end=" | ")
                for program in program_group:
                    lang = program.lang
                    result = all_results[program.basename][group][test]
                    print(("%23s" % color_memory(result.Memory,
                                                 package_util.get_memory_limit(test, config, lang, task_id, args)))
                          if result.Memory is not None else 13 * " ", end=" | ")
                print()

        print_table_end()
        print()

    sys.stdout = previous_stdout
    return output.getvalue().splitlines(), title, "Use arrows to move."
