# Modified version of https://sinol3.dasie.mimuw.edu.pl/oij/jury/package/-/blob/master/runner.py
# Author of the original code: Bartosz Kostka <kostka@oij.edu.pl>
# Version 0.6 (2021-08-29)
import threading
import glob
import shutil
import os
import collections
import sys
import math
import dictdiffer
import multiprocessing as mp
from io import StringIO
from typing import Dict

from sinol_make import contest_types, util, sio2jail
from sinol_make.structs.run_structs import ExecutionData, PrintData
from sinol_make.structs.cache_structs import CacheTest, CacheFile
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.interfaces.Errors import CompilationError, UnknownContestType
from sinol_make.helpers import compile, compiler, package_util, printer, paths, cache, parsers
from sinol_make.structs.status_structs import Status, ResultChange, PointsChange, ValidationResult, ExecutionResult, \
    TotalPointsChange


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
    if time > limit:
        return util.color_red(time_str)
    elif time > limit / 2.0:
        return util.color_yellow(time_str)
    else:
        return util.color_green(time_str)


def colorize_status(status):
    if status == Status.OK: return util.bold(util.color_green(status))
    if status == Status.PENDING: return util.warning(status)
    return util.error(status)


def colorize_points(points, min_points, max_points):
    if points == max_points:
        return util.color_green(str(points))
    elif points == min_points:
        return util.color_red(str(points))
    else:
        return util.color_yellow(str(points))


def update_group_status(group_status, new_status):
    order = [Status.CE, Status.TL, Status.ML, Status.RE, Status.WA, Status.OK, Status.PENDING]
    if order.index(new_status) < order.index(group_status):
        return new_status
    return group_status


def print_view(term_width, term_height, task_id, program_groups_scores, all_results, print_data: PrintData, names, executions,
               groups, scores, tests, possible_score, cpus, hide_memory, config, contest, args):
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
    for solution in names:
        lang = package_util.get_file_lang(solution)
        for test in tests:
            time_sum += package_util.get_time_limit(test, config, lang, task_id, args)

    time_remaining = (len(executions) - print_data.i - 1) * 2 * time_sum / cpus / 1000.0
    title = 'Done %4d/%4d. Time remaining (in the worst case): %5d seconds.' \
            % (print_data.i + 1, len(executions), time_remaining)
    title = title.center(term_width)
    margin = "  "
    for program_ix in range(0, len(names), programs_in_row):
        program_group = names[program_ix:program_ix + programs_in_row]

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
        next_row = {solution: solution for solution in program_group}
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
                lang = package_util.get_file_lang(program)
                results = all_results[program][group]
                group_status = Status.OK
                test_scores = []

                for test in results:
                    test_scores.append(results[test].Points)
                    status = results[test].Status
                    if results[test].Time is not None:
                        if program_times[program][0] < results[test].Time:
                            program_times[program] = (results[test].Time, package_util.get_time_limit(test, config,
                                                                                                      lang, task_id, args))
                    elif status == Status.TL:
                        program_times[program] = (2 * package_util.get_time_limit(test, config, lang, task_id, args),
                                                  package_util.get_time_limit(test, config, lang, task_id, args))
                    if results[test].Memory is not None:
                        if program_memory[program][0] < results[test].Memory:
                            program_memory[program] = (results[test].Memory, package_util.get_memory_limit(test, config,
                                                                                                           lang, task_id, args))
                    elif status == Status.ML:
                        program_memory[program] = (2 * package_util.get_memory_limit(test, config, lang, task_id, args),
                                                   package_util.get_memory_limit(test, config, lang, task_id, args))
                    if status == Status.PENDING:
                        group_status = Status.PENDING
                    else:
                        group_status = update_group_status(group_status, status)

                points = contest.get_group_score(test_scores, scores[group])
                if any([results[test].Status == Status.PENDING for test in results]):
                    print(" " * 6 + ("?" * len(str(scores[group]))).rjust(3) +
                          f'/{str(scores[group]).rjust(3)}', end=' | ')
                else:
                    if group_status == Status.OK:
                        status_text = util.bold(util.color_green(group_status.ljust(6)))
                    else:
                        status_text = util.bold(util.color_red(group_status.ljust(6)))
                    print(f"{status_text}{str(int(points)).rjust(3)}/{str(scores[group]).rjust(3)}", end=' | ')
                program_groups_scores[program][group] = {"status": group_status, "points": points}
            print()
        for program in program_group:
            program_scores[program] = contest.get_global_score(program_groups_scores[program], possible_score)

        print(8 * " ", end=" | ")
        for program in program_group:
            print(13 * " ", end=" | ")
        print()
        print(margin + "points", end=" | ")
        for program in program_group:
            print(util.bold("      %3s/%3s" % (program_scores[program], possible_score)), end=" | ")
        print()
        print(margin + "  time", end=" | ")
        for program in program_group:
            program_time = program_times[program]
            print(util.bold(("%23s" % color_time(program_time[0], program_time[1]))
                            if program_time[0] < 2 * program_time[1] and program_time[0] >= 0
                            else "      " + 7 * '-'), end=" | ")
        print()
        print(margin + "memory", end=" | ")
        for program in program_group:
            program_mem = program_memory[program]
            print(util.bold(("%23s" % color_memory(program_mem[0], program_mem[1]))
                            if program_mem[0] < 2 * program_mem[1] and program_mem[0] >= 0
                            else "      " + 7 * '-'), end=" | ")
        print()
        print(8*" ", end=" | ")
        for program in program_group:
            print(13*" ", end=" | ")
        print()

        def print_group_seperator():
            print(8 * "-", end=" | ")
            for program in program_group:
                print(13 * "-", end=" | ")
            print()

        print_group_seperator()

        last_group = None
        for test in tests:
            group = package_util.get_group(test, task_id)
            if last_group != group:
                if last_group is not None:
                    print_group_seperator()
                last_group = group

            print(margin + "%6s" % package_util.extract_test_id(test, task_id), end=" | ")
            for program in program_group:
                lang = package_util.get_file_lang(program)
                result = all_results[program][package_util.get_group(test, task_id)][test]
                status = result.Status
                if status == Status.PENDING: print(13 * ' ', end=" | ")
                else:
                    print("%3s" % colorize_status(status),
                         ("%20s" % color_time(result.Time, package_util.get_time_limit(test, config, lang, task_id, args)))
                         if result.Time is not None else 10*" ", end=" | ")
            print()
            if not hide_memory:
                print(8*" ", end=" | ")
                for program in program_group:
                    lang = package_util.get_file_lang(program)
                    result = all_results[program][package_util.get_group(test, task_id)][test]
                    if result.Status != Status.PENDING:
                        print(colorize_points(int(result.Points), contest.min_score_per_test(),
                                              contest.max_score_per_test()).ljust(13), end="")
                    else:
                        print(3*" ", end="")
                    print(("%20s" % color_memory(result.Memory, package_util.get_memory_limit(test, config, lang, task_id, args)))
                          if result.Memory is not None else 10*" ", end=" | ")
                print()

        print_table_end()
        print()

    sys.stdout = previous_stdout
    return output.getvalue().splitlines(), title, "Use arrows to move."


class Command(BaseCommand):
    """
    Class for running current task
    """

    def get_name(self):
        return 'run'

    def get_short_name(self):
        return 'r'

    def configure_subparser(self, subparser):
        parser = subparser.add_parser(
            'run',
            help='Runs solutions in parallel on tests and verifies the expected solutions\' scores with the config.',
            description='Runs selected solutions (by default all solutions) \
                on selected tests (by default all tests) \
                with a given number of cpus. \
                Measures the solutions\' time with sio2jail, unless specified otherwise. \
                After running the solutions, it compares the solutions\' scores with the ones saved in config.yml.'
        )

        default_timetool = 'sio2jail' if sio2jail.sio2jail_supported() else 'time'

        parser.add_argument('-s', '--solutions', type=str, nargs='+',
                            help='solutions to be run, for example prog/abc{b,s}*.{cpp,py}')
        parser.add_argument('-t', '--tests', type=str, nargs='+',
                            help='tests to be run, for example in/abc{0,1}*')
        parsers.add_cpus_argument(parser, 'number of cpus to use when running solutions')
        parser.add_argument('--tl', type=float, help='time limit for all tests (in s)')
        parser.add_argument('--ml', type=float, help='memory limit for all tests (in MB)')
        parser.add_argument('--hide-memory', dest='hide_memory', action='store_true',
                            help='hide memory usage in report')
        parser.add_argument('-T', '--time-tool', dest='time_tool', choices=['sio2jail', 'time'],
                            help=f'tool to measure time and memory usage (default: {default_timetool})')
        parser.add_argument('--sio2jail-path', dest='sio2jail_path', type=str,
                            help='path to sio2jail executable (default: `~/.local/bin/sio2jail`)')
        parser.add_argument('-a', '--apply-suggestions', dest='apply_suggestions', action='store_true',
                            help='apply suggestions from expected scores report')
        parser.add_argument('--ignore-expected', dest='ignore_expected', action='store_true',
                            help='ignore expected scores from config.yml. When this flag is set, '
                                 'the expected scores are not compared with the actual scores.')
        parser.add_argument('--no-outputs', dest='allow_no_outputs', action='store_true',
                            help='allow running the script without full outputs')
        parser.add_argument('-o', '--comments', dest='comments', action='store_true',
                            help="show checker's comments")
        parsers.add_compilation_arguments(parser)
        return parser

    def extract_file_name(self, file_path):
        return os.path.split(file_path)[1]

    def get_group(self, test_path):
        return package_util.get_group(test_path, self.ID)

    def get_solution_from_exe(self, executable):
        file = os.path.splitext(executable)[0]
        for ext in self.SOURCE_EXTENSIONS:
            if os.path.isfile(os.path.join(os.getcwd(), "prog", file + ext)):
                return file + ext
        util.exit_with_error("Source file not found for executable %s" % executable)

    def get_possible_score(self, groups):
        possible_score = 0
        for group in groups:
            possible_score += self.scores[group]
        return possible_score

    def get_groups(self, tests):
        return sorted(list(set([self.get_group(test) for test in tests])))

    def compile_solutions(self, solutions):
        print("Compiling %d solutions..." % len(solutions))
        args = [(solution, None, True, False, None) for solution in solutions]
        with mp.Pool(self.cpus) as pool:
            compilation_results = pool.starmap(self.compile, args)
        return compilation_results

    def compile(self, solution, dest=None, use_extras=False, clear_cache=False, name=None):
        compile_log_file = paths.get_compilation_log_path("%s.compile_log" % package_util.get_file_name(solution))
        source_file = os.path.join(os.getcwd(), "prog", self.get_solution_from_exe(solution))
        if dest:
            output = dest
        else:
            output = paths.get_executables_path(package_util.get_executable(solution))
        name = name or "file " + package_util.get_file_name(solution)

        extra_compilation_args = []
        extra_compilation_files = []
        if use_extras:
            lang = os.path.splitext(source_file)[1][1:]
            args = self.config.get("extra_compilation_args", {}).get(lang, [])
            if isinstance(args, str):
                args = [args]
            for arg in args:
                path = os.path.join(os.getcwd(), "prog", arg)
                if os.path.exists(path):
                    extra_compilation_args.append(path)
                else:
                    extra_compilation_args.append(arg)

            for file in self.config.get("extra_compilation_files", []):
                extra_compilation_files.append(os.path.join(os.getcwd(), "prog", file))

        try:
            with open(compile_log_file, "w") as compile_log:
                compile.compile(source_file, output, self.compilers, compile_log, self.args.compile_mode,
                                extra_compilation_args, extra_compilation_files, clear_cache=clear_cache)
            print(util.info(f"Compilation of {name} was successful."))
            return True
        except CompilationError as e:
            print(util.error(f"Compilation of {name} was unsuccessful."))
            compile.print_compile_log(compile_log_file)
            return False

    def run_solution(self, data_for_execution: ExecutionData):
        """
        Run an execution and return the result as ExecutionResult object.
        """

        (name, executable, test, time_limit, memory_limit, timetool_path, execution_dir) = data_for_execution
        file_no_ext = paths.get_executions_path(name, package_util.extract_test_id(test, self.ID))
        output_file = file_no_ext + ".out"
        result_file = file_no_ext + ".res"
        hard_time_limit = math.ceil(2 * time_limit / 1000.0)

        return self.task_type.run(time_limit, hard_time_limit, memory_limit, test, output_file,
                                  package_util.get_out_from_in(test), result_file, executable, execution_dir)

    def run_solutions(self, compiled_commands, names, solutions, executables_dir):
        """
        Run solutions on tests and print the results as a table to stdout.
        """

        executions = []
        all_cache_files: Dict[str, CacheFile] = {}
        all_results = collections.defaultdict(
            lambda: collections.defaultdict(lambda: collections.defaultdict(map)))

        for lang, files in self.config.get('extra_execution_files', {}).items():
            for file in files:
                shutil.copy(os.path.join(os.getcwd(), "prog", file), executables_dir)
        # Copy swig generated .so files
        for file in glob.glob(os.path.join(os.getcwd(), "prog", f"_{self.ID}lib.so")):
            shutil.copy(file, executables_dir)

        for (name, executable, result) in compiled_commands:
            lang = package_util.get_file_lang(name)
            solution_cache = cache.get_cache_file(os.path.join(os.getcwd(), "prog", name))
            all_cache_files[name] = solution_cache

            if result:
                for test in self.tests:
                    test_time_limit = package_util.get_time_limit(test, self.config, lang, self.ID, self.args)
                    test_memory_limit = package_util.get_memory_limit(test, self.config, lang, self.ID, self.args)

                    test_result: CacheTest = solution_cache.tests.get(self.test_md5sums[os.path.basename(test)], None)
                    if test_result is not None and test_result.time_limit == test_time_limit and \
                            test_result.memory_limit == test_memory_limit and \
                            test_result.time_tool == self.timetool_name:
                        all_results[name][self.get_group(test)][test] = test_result.result
                    else:
                        executions.append((name, executable, test, test_time_limit, test_memory_limit,
                                           self.timetool_path, os.path.dirname(executable)))
                        all_results[name][self.get_group(test)][test] = ExecutionResult(Status.PENDING)
                os.makedirs(paths.get_executions_path(name), exist_ok=True)
            else:
                for test in self.tests:
                    all_results[name][self.get_group(test)][test] = ExecutionResult(Status.CE)
        print()
        executions.sort(key = lambda x: (package_util.get_executable_key(x[1], self.ID), x[2]))
        program_groups_scores = collections.defaultdict(dict)
        print_data = PrintData(0)

        has_terminal, terminal_width, terminal_height = util.get_terminal_size()

        if has_terminal:
            run_event = threading.Event()
            run_event.set()
            thr = threading.Thread(target=printer.printer_thread,
                                   args=(run_event, print_view, self.ID, program_groups_scores, all_results, print_data,
                                         names, executions, self.groups, self.scores, self.tests, self.possible_score,
                                         self.cpus, self.args.hide_memory, self.config, self.contest, self.args))
            thr.start()

        pool = mp.Pool(self.cpus)
        keyboard_interrupt = False
        try:
            for i, result in enumerate(pool.imap(self.run_solution, executions)):
                (name, executable, test, time_limit, memory_limit) = executions[i][:5]
                contest_points = self.contest.get_test_score(result, time_limit, memory_limit)
                result.Points = contest_points
                all_results[name][self.get_group(test)][test] = result
                print_data.i = i

                # We store the result in dictionary to write it to cache files later.
                lang = package_util.get_file_lang(name)
                test_time_limit = package_util.get_time_limit(test, self.config, lang, self.ID, self.args)
                test_memory_limit = package_util.get_memory_limit(test, self.config, lang, self.ID, self.args)
                all_cache_files[name].tests[self.test_md5sums[os.path.basename(test)]] = CacheTest(
                    time_limit=test_time_limit,
                    memory_limit=test_memory_limit,
                    time_tool=self.timetool_name,
                    result=result
                )
            pool.terminate()
        except KeyboardInterrupt:
            keyboard_interrupt = True
            pool.terminate()
        finally:
            if has_terminal:
                run_event.clear()
                thr.join()

        print("\n".join(print_view(terminal_width, terminal_height, self.ID, program_groups_scores, all_results, print_data,
                                   names, executions, self.groups, self.scores, self.tests, self.possible_score,
                                   self.cpus, self.args.hide_memory, self.config, self.contest, self.args)[0]))

        # Write cache files.
        for solution, cache_data in all_cache_files.items():
            cache_data.save(os.path.join(os.getcwd(), "prog", solution))

        if keyboard_interrupt:
            util.exit_with_error("Stopped due to keyboard interrupt.")

        return program_groups_scores, all_results

    def compile_and_run(self, solutions):
        compilation_results = self.compile_solutions(solutions)
        for i in range(len(solutions)):
            if not compilation_results[i]:
                self.failed_compilations.append(solutions[i])
        executables = [paths.get_executables_path(package_util.get_executable(solution)) for solution in solutions]
        compiled_commands = zip(solutions, executables, compilation_results)
        names = solutions
        return self.run_solutions(compiled_commands, names, solutions, paths.get_executables_path())

    def convert_status_to_string(self, dictionary):
        """
        Converts all `Status` enums in dict to strings.
        """
        def _convert(obj):
            if isinstance(obj, dict):
                return { k: _convert(v) for k, v in obj.items() }
            elif isinstance(obj, list):
                return [ _convert(v) for v in obj ]
            elif isinstance(obj, Status):
                return obj.name
            else:
                return obj
        return _convert(dictionary)

    def get_whole_groups(self):
        """
        Returns a list of groups for which all tests were run.
        """
        group_sizes = {}
        for test in package_util.get_tests(self.ID):
            group = package_util.get_group(test, self.ID)
            if group not in group_sizes:
                group_sizes[group] = 0
            group_sizes[group] += 1

        run_group_sizes = {}
        for test in self.tests:
            group = package_util.get_group(test, self.ID)
            if group not in run_group_sizes:
                run_group_sizes[group] = 0
            run_group_sizes[group] += 1

        whole_groups = []
        for group in group_sizes.keys():
            if group in run_group_sizes and group_sizes[group] == run_group_sizes[group]:
                whole_groups.append(group)
        return whole_groups

    def validate_expected_scores(self, results):
        new_expected_scores = {} # Expected scores based on results

        for solution in results.keys():
            for group in results[solution].keys():
                if group not in self.scores:
                    util.exit_with_error(f'Group {group} doesn\'t have points specified in config file.')

        for solution in results.keys():
            new_expected_scores[solution] = {
                "expected": results[solution],
                "points": self.contest.get_global_score(results[solution], self.possible_score)
            }

        config_expected_scores = self.config.get("sinol_expected_scores", {})
        used_solutions = results.keys()
        if self.args.solutions is None and config_expected_scores:  # If no solutions were specified, use all solutions from config
            used_solutions = config_expected_scores.keys()
        used_solutions = list(used_solutions)

        for solution in self.failed_compilations:
            if solution in used_solutions:
                used_solutions.remove(solution)

        used_groups = set()
        if self.args.tests == None and config_expected_scores: # If no groups were specified, use all groups from config
            for solution in config_expected_scores.keys():
                used_groups.update(config_expected_scores[solution]["expected"].keys())
        else:
            used_groups = self.get_whole_groups()

            # This removes those groups from `new_expected_scores` that have not been run.
            # Then, if there are any solutions for which no groups have been run, they are also removed.
            solutions_to_delete = []
            for solution in new_expected_scores.keys():
                groups_to_remove = []
                for group in new_expected_scores[solution]["expected"]:
                    if group not in used_groups:
                        groups_to_remove.append(group)
                for group in groups_to_remove:
                    del new_expected_scores[solution]["expected"][group]

                # If there are no groups left, remove the solution.
                if len(new_expected_scores[solution]["expected"]) == 0:
                    solutions_to_delete.append(solution)
            for solution in solutions_to_delete:
                del new_expected_scores[solution]

        used_groups = list(used_groups)

        expected_scores = {} # Expected scores from config with only solutions and groups that were run
        for solution in used_solutions:
            if solution in config_expected_scores.keys():
                expected_scores[solution] = {
                    "expected": {},
                    "points": 0
                }

                for group in used_groups:
                    if group in config_expected_scores[solution]["expected"]:
                        expected_scores[solution]["expected"][group] = config_expected_scores[solution]["expected"][group]

                expected_scores[solution]["points"] = self.contest.get_global_score(expected_scores[solution]["expected"],
                                                                                    self.possible_score)
                if len(expected_scores[solution]["expected"]) == 0:
                    del expected_scores[solution]

        expected_scores_diff = dictdiffer.diff(expected_scores, new_expected_scores)
        added_solutions = set()
        removed_solutions = set()
        added_groups = set()
        removed_groups = set()
        changes = []
        unknown_change = False

        for type, field, change in list(expected_scores_diff):
            if type == "add":
                if field == '': # Solutions were added
                    for solution in change:
                        added_solutions.add(solution[0])
                elif field[1] == "expected": # Groups were added
                    for group in change:
                        added_groups.add(group[0])
            elif type == "remove":
                # We check whether a solution was removed only when sinol_make was run on all of them
                if field == '' and self.args.solutions == None and config_expected_scores:
                    for solution in change:
                        removed_solutions.add(solution[0])
                # We check whether a group was removed only when sinol_make was run on all of them
                elif field[1] == "expected" and self.args.tests == None and config_expected_scores:
                    for group in change:
                        removed_groups.add(group[0])
            elif type == "change":
                if field[1] == "expected": # Results for at least one group has changed
                    solution = field[0]
                    group = field[2]
                    if isinstance(change[0], str) and isinstance(change[1], dict):
                        changes.append(PointsChange(
                            solution=solution,
                            group=group,
                            old_points=self.scores[field[2]],
                            new_points=change[1]["points"]
                        ))
                    elif isinstance(change[0], dict) and isinstance(change[1], str):
                        changes.append(PointsChange(
                            solution=solution,
                            group=group,
                            old_points=change[0]["points"],
                            new_points=self.scores[field[2]]
                        ))
                    elif isinstance(change[0], dict) and isinstance(change[1], dict):
                        changes.append(PointsChange(
                            solution=solution,
                            group=group,
                            old_points=change[0]["points"],
                            new_points=change[1]["points"]
                        ))
                    else:
                        changes.append(ResultChange(
                            solution=solution,
                            group=group,
                            old_result=change[0],
                            result=change[1]
                        ))
                elif field[1] == "points": # Points for at least one solution has changed
                    solution = field[0]
                    changes.append(TotalPointsChange(
                        solution=solution,
                        old_points=change[0],
                        new_points=change[1]
                    ))
                else:
                    unknown_change = True


        return ValidationResult(
            added_solutions,
            removed_solutions,
            added_groups,
            removed_groups,
            changes,
            expected_scores,
            new_expected_scores,
            unknown_change,
        )

    def print_expected_scores_diff(self, validation_results: ValidationResult):
        diff = validation_results
        config_expected_scores = self.config.get("sinol_expected_scores", {})

        if diff.unknown_change:
            print(util.error("There was an unknown change in expected scores. "
                             "You should apply the suggested changes to avoid errors."))

        def warn_if_not_empty(set, message):
            if len(set) > 0:
                print(util.warning(message + ": "), end='')
                print(util.warning(", ".join([str(x) for x in set])))

        warn_if_not_empty(diff.added_solutions, "Solutions were added")
        warn_if_not_empty(diff.removed_solutions, "Solutions were removed")
        warn_if_not_empty(diff.added_groups, "Groups were added")
        warn_if_not_empty(diff.removed_groups, "Groups were removed")

        for change in diff.changes:
            def print_points_change(solution, group, new_points, old_points):
                print(util.warning("Solution %s passed group %d with %d points while it should pass with %d points." %
                                   (solution, group, new_points, old_points)))

            if isinstance(change, ResultChange):
                if isinstance(change.result, str):
                    print(util.warning("Solution %s passed group %d with status %s while it should pass with status %s." %
                                       (change.solution, change.group, change.result, change.old_result)))
                elif isinstance(change.result, int):
                    print_points_change(change.solution, change.group, change.result, change.old_result)
            elif isinstance(change, PointsChange):
                print_points_change(change.solution, change.group, change.new_points, change.old_points)
            elif isinstance(change, TotalPointsChange):
                print(util.warning("Solution %s passed all groups with %d points while it should pass with %d points." %
                                   (change.solution, change.new_points, change.old_points)))

        if diff.expected_scores == diff.new_expected_scores and not diff.unknown_change:
            print(util.info("Expected scores are correct!"))
        else:
            def delete_group(solution, group):
                if group in config_expected_scores[solution]["expected"]:
                    del config_expected_scores[solution]["expected"][group]
                    config_expected_scores[solution]["points"] = self.contest.get_global_score(
                        config_expected_scores[solution]["expected"],
                        self.possible_score
                    )

            def set_group_result(solution, group, result):
                config_expected_scores[solution]["expected"][group] = result
                config_expected_scores[solution]["points"] = self.contest.get_global_score(
                    config_expected_scores[solution]["expected"],
                    self.possible_score
                )

            if self.args.apply_suggestions:
                for solution in diff.removed_solutions:
                    del config_expected_scores[solution]

                for solution in config_expected_scores:
                    for group in diff.removed_groups:
                        delete_group(solution, group)

                for solution in diff.new_expected_scores.keys():
                    if solution in config_expected_scores:
                        for group, result in diff.new_expected_scores[solution]["expected"].items():
                            set_group_result(solution, group, result)
                    else:
                        config_expected_scores[solution] = diff.new_expected_scores[solution]

                self.config["sinol_expected_scores"] = self.convert_status_to_string(config_expected_scores)
                util.save_config(self.config)
                print("Saved suggested expected scores description.")
            else:
                util.exit_with_error("Use flag --apply-suggestions to apply suggestions.")

    def set_constants(self):
        self.ID = package_util.get_task_id()
        self.SOURCE_EXTENSIONS = ['.c', '.cpp', '.py', '.java']
        self.SOLUTIONS_RE = package_util.get_solutions_re(self.ID)

    def validate_arguments(self, args):
        compilers = compiler.verify_compilers(args, package_util.get_solutions(self.ID, None))

        def use_sio2jail():
            timetool_path = None
            if not sio2jail.sio2jail_supported():
                util.exit_with_error('As `sio2jail` works only on Linux-based operating systems,\n'
                                     'we do not recommend using operating systems such as macOS.\n'
                                     'Nevertheless, you can still run sinol-make by specifying\n'
                                     'another way of measuring time through the `--time-tool` flag.\n'
                                     'See `sinol-make run --help` for more information about the flag.\n'
                                     'See https://github.com/sio2project/sinol-make#why for more information about `sio2jail`.\n')

            sio2jail.check_perf_counters_enabled()
            if 'sio2jail_path' in args and args.sio2jail_path is not None:
                if not sio2jail.check_sio2jail(args.sio2jail_path):
                    util.exit_with_error('Invalid `sio2jail` path.')
                timetool_path = args.sio2jail_path
            else:
                timetool_path = sio2jail.get_default_sio2jail_path()
            if timetool_path is None:
                util.exit_with_error('`sio2jail` is not installed.')
            return timetool_path, 'sio2jail'
        def use_time():
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                util.exit_with_error('Measuring with `time` is not supported on Windows.')
            return 'time', 'time'

        timetool_path, timetool_name = None, None
        preferred_timetool = self.contest.preferred_timetool()
        if preferred_timetool == 'sio2jail' and sio2jail.sio2jail_supported():
            use_default_timetool = use_sio2jail
        elif preferred_timetool == 'time':
            use_default_timetool = use_time
        else:
            use_default_timetool = use_sio2jail if sio2jail.sio2jail_supported() else use_time

        if args.time_tool is None and self.config.get('sinol_undocumented_time_tool', '') != '':
            if self.config.get('sinol_undocumented_time_tool', '') == 'sio2jail':
                timetool_path, timetool_name = use_sio2jail()
            elif self.config.get('sinol_undocumented_time_tool', '') == 'time':
                timetool_path, timetool_name = use_time()
            else:
                util.exit_with_error('Invalid time tool specified in config.yml.')
        elif args.time_tool is None:
            timetool_path, timetool_name = use_default_timetool()
        elif args.time_tool == 'sio2jail':
            timetool_path, timetool_name = use_sio2jail()
        elif args.time_tool == 'time':
            timetool_path, timetool_name = use_time()
        else:
            util.exit_with_error('Invalid time tool specified.')
        return compilers, timetool_path, timetool_name

    def exit(self):
        if len(self.failed_compilations) > 0:
            util.exit_with_error('Compilation failed for {cnt} solution{letter}.'.format(
                cnt=len(self.failed_compilations), letter='' if len(self.failed_compilations) == 1 else 's'))

    def set_scores(self):
        self.groups = self.get_groups(self.tests)
        self.scores = collections.defaultdict(int)

        if 'scores' not in self.config.keys():
            self.scores = self.contest.assign_scores(self.groups)
        else:
            total_score = 0
            for group in self.config["scores"]:
                self.scores[group] = self.config["scores"][group]
                total_score += self.scores[group]

            if total_score != 100:
                print(util.warning("WARN: Scores sum up to %d instead of 100." % total_score))
                print()

        self.possible_score = self.contest.get_possible_score(self.groups, self.scores)

    def get_valid_input_files(self):
        """
        Returns list of input files that have corresponding output file.
        """
        output_tests = glob.glob(os.path.join(os.getcwd(), "out", "*.out"))
        output_tests_ids = [package_util.extract_test_id(test, self.ID) for test in output_tests]
        valid_input_files = []
        for test in self.tests:
            if package_util.extract_test_id(test, self.ID) in output_tests_ids:
                valid_input_files.append(test)
        return valid_input_files

    def validate_existence_of_outputs(self):
        """
        Checks if all input files have corresponding output files.
        """
        valid_input_files = self.get_valid_input_files()
        if len(valid_input_files) != len(self.tests):
            missing_tests = list(set(self.tests) - set(valid_input_files))
            missing_tests.sort()

            print(util.warning('Missing output files for tests: ' + ', '.join(
                [self.extract_file_name(test) for test in missing_tests])))
            if not self.args.allow_no_outputs:
                util.exit_with_error('There are tests without outputs. \n'
                                     'Run outgen to fix this issue or add the --no-outputs flag to ignore the issue.')
            print(util.warning('Running only on tests with output files.'))
            self.tests = valid_input_files
            self.groups = self.get_groups(self.tests)
            if len(self.groups) < 1:
                util.exit_with_error('No tests with valid outputs.')

    def check_are_any_tests_to_run(self):
        """
        Checks if there are any tests to run and prints them and checks
        if all input files have corresponding output files.
        """
        if len(self.tests) > 0:
            print(util.bold('Tests that will be run:'), ' '.join([self.extract_file_name(test) for test in self.tests]))

            example_tests = [test for test in self.tests if self.get_group(test) == 0]
            if len(example_tests) == len(self.tests):
                print(util.warning('Running only on example tests.'))

            if not self.has_lib and self.task_type.run_outgen():
                self.validate_existence_of_outputs()
        else:
            util.exit_with_error('There are no tests to run.')

    def check_errors(self, results: Dict[str, Dict[str, Dict[str, ExecutionResult]]]):
        """
        Checks if there were any errors during execution and exits if there were.
        :param results: Dictionary of results.
        :return:
        """
        error_msg = ""
        fail = False
        for solution in results:
            for group in results[solution]:
                for test in results[solution][group]:
                    if results[solution][group][test].Error is not None:
                        error_msg += (f'Solution {solution} had an error on test {test}: '
                                      f'{results[solution][group][test].Error}')
                        if results[solution][group][test].Stderr != ['']:
                            error_msg += f' Stderr:\n{results[solution][group][test].Stderr}'
                        error_msg += '\n'
                        fail |= results[solution][group][test].Fail
        if error_msg != "":
            print(util.error(error_msg))
            if fail:
                sys.exit(1)

    def print_checker_comments(self, results: Dict[str, Dict[str, Dict[str, ExecutionResult]]]):
        """
        Prints checker's comments for all tests and solutions.
        """
        print(util.bold("Checker comments:"))
        any_comments = False
        for solution in results:
            for group in results[solution]:
                for test in results[solution][group]:
                    result = results[solution][group][test]
                    if result.Comment != "":
                        any_comments = True
                        print(util.bold(f"{solution} on {test}: ") + result.Comment)
        if not any_comments:
            print("No comments.")

    def set_task_type(self, timetool_name, timetool_path):
        self.task_type = package_util.get_task_type(timetool_name, timetool_path)

    def compile_additional_files(self):
        additional_files = self.task_type.additional_files_to_compile()
        for file, dest, name, clear_cache, fail_on_error in additional_files:
            print(f"Compiling {name}...")
            success = self.compile(file, dest, False, clear_cache, name)
            if not success and fail_on_error:
                sys.exit(1)

    def run(self, args):
        args = util.init_package_command(args)

        self.set_constants()
        package_util.validate_test_names(self.ID)
        self.args = args
        self.config = package_util.get_config()
        try:
            self.contest = contest_types.get_contest_type()
        except UnknownContestType as e:
            util.exit_with_error(str(e))

        if not 'title' in self.config.keys():
            util.exit_with_error('Title was not defined in config.yml.')

        self.compilers, self.timetool_path, self.timetool_name = self.validate_arguments(args)

        title = self.config["title"]
        print("Task: %s (tag: %s)" % (title, self.ID))
        self.cpus = args.cpus or util.default_cpu_count()
        cache.process_extra_compilation_files(self.config.get("extra_compilation_files", []), self.ID)
        cache.process_extra_execution_files(self.config.get("extra_execution_files", {}), self.ID)
        cache.remove_results_if_contest_type_changed(self.config.get("sinol_contest_type", "default"))

        self.set_task_type(self.timetool_name, self.timetool_path)
        self.compile_additional_files()

        lib = package_util.get_files_matching_pattern(self.ID, f'{self.ID}lib.*')
        self.has_lib = len(lib) != 0

        self.tests = package_util.get_tests(self.ID, self.args.tests)
        self.test_md5sums = {os.path.basename(test): util.get_file_md5(test) for test in self.tests}
        self.check_are_any_tests_to_run()
        self.set_scores()
        self.failed_compilations = []
        solutions = package_util.get_solutions(self.ID, self.args.solutions)

        util.change_stack_size_to_unlimited()
        for solution in solutions:
            lang = package_util.get_file_lang(solution)
            for test in self.tests:
                # The functions will exit if the limits are not set
                _ = package_util.get_time_limit(test, self.config, lang, self.ID, self.args)
                _ = package_util.get_memory_limit(test, self.config, lang, self.ID, self.args)

        results, all_results = self.compile_and_run(solutions)
        self.check_errors(all_results)
        if self.args.comments:
            self.print_checker_comments(all_results)
        if self.args.ignore_expected:
            print(util.warning("Ignoring expected scores."))
            self.exit()
            return

        try:
            validation_results = self.validate_expected_scores(results)
        except:
            self.config = util.try_fix_config(self.config)
            try:
                validation_results = self.validate_expected_scores(results)
            except:
                util.exit_with_error("Validating expected scores failed. "
                                     "This probably means that `sinol_expected_scores` is broken. "
                                     "Delete it and run `sinol-make run --apply-suggestions` again.")
        self.print_expected_scores_diff(validation_results)
        self.exit()
