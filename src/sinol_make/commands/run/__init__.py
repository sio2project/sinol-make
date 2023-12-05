# Modified version of https://sinol3.dasie.mimuw.edu.pl/oij/jury/package/-/blob/master/runner.py
# Author of the original code: Bartosz Kostka <kostka@oij.edu.pl>
# Version 0.6 (2021-08-29)
import threading
import subprocess
import os
import collections
import dictdiffer
import multiprocessing as mp
from typing import Dict, List, Tuple

from sinol_make import contest_types
from sinol_make.commands.run.run_util import print_view
from sinol_make.programs.solution import Solution
from sinol_make.structs.run_structs import PrintData, RunExecution
from sinol_make.structs.cache_structs import CacheTest, CacheFile
from sinol_make.helpers.parsers import add_compilation_arguments
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.interfaces.Errors import CheckerOutputException, UnknownContestType
from sinol_make.helpers import package_util, printer, paths, cache
from sinol_make.structs.status_structs import (
    Status,
    ResultChange,
    PointsChange,
    ValidationResult,
    ExecutionResult,
    TotalPointsChange
)
from sinol_make.structs.timetool_structs import TimeToolResult
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest
from sinol_make import util


class Command(BaseCommand):
    """
    Class for running current task
    """

    def get_name(self):
        return 'run'

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

        parser.add_argument('-s', '--solutions', type=str, nargs='+',
                            help='solutions to be run, for example prog/abc{b,s}*.{cpp,py}')
        parser.add_argument('-t', '--tests', type=str, nargs='+',
                            help='tests to be run, for example in/abc{0,1}*')
        parser.add_argument('-c', '--cpus', type=int,
                            help=f'number of cpus to use (default: {util.default_cpu_count()}')
        parser.add_argument('--tl', type=float, help='time limit for all tests (in s)')
        parser.add_argument('--ml', type=float, help='memory limit for all tests (in MB)')
        parser.add_argument('--hide-memory', dest='hide_memory', action='store_true',
                            help='hide memory usage in report')
        self.timetool_manager.add_arg(parser)
        parser.add_argument('-a', '--apply-suggestions', dest='apply_suggestions', action='store_true',
                            help='apply suggestions from expected scores report')
        add_compilation_arguments(parser)

    def get_possible_score(self, groups):
        possible_score = 0
        for group in groups:
            possible_score += self.scores[group]
        return possible_score

    def get_groups(self, tests):
        return sorted(list(set([test.group for test in tests])))

    def compile_solutions(self, solutions: List[Solution]):
        print("Compiling %d solutions..." % len(solutions))
        with mp.Pool(self.cpus) as pool:
            compilation_results = pool.map(self.compile, solutions)
        return compilation_results

    def compile(self, solution: Solution):
        exe, compile_log = solution.compile()
        if exe is None:
            print(util.error(f"Compilation of file {solution.basename} was unsuccessful."))
            self.compiler_manager.print_compile_log(compile_log)
            return False
        else:
            print(util.info(f"Compilation of file {solution.basename} was successful."))
            return True

    def check_output(self, input_test: InputTest, output_file: str, output_test: OutputTest):
        """
        Checks if the output file is correct.
        Returns a tuple (is correct, number of points).
        """
        try:
            has_checker = self.checker is not None
        except AttributeError:
            has_checker = False

        if not has_checker:
            correct = util.file_diff(output_test.file_path, output_file)
            return correct, 100 if correct else 0
        else:
            return self.checker.check_output(input_test, output_file, output_test)

    def run_solution(self, data_for_execution: RunExecution) -> ExecutionResult:
        """
        Run an execution and return the result as ExecutionResult object.
        """
        solution = data_for_execution.solution
        test = data_for_execution.test
        time_limit = data_for_execution.time_limit
        memory_limit = data_for_execution.memory_limit
        file_no_ext = paths.get_executions_path(solution.basename, test.test_id)
        output_path = file_no_ext + ".out"
        result_path = file_no_ext + ".res"

        with test.open("r") as input_file, open(output_path, "w") as output_file:
            res: TimeToolResult = self.timetool_manager.run([solution.executable_path], result_path,
                                                            stdin=input_file, stdout=output_file, stderr=subprocess.STDOUT,
                                                            time_limit=time_limit, memory_limit=memory_limit)

        result = ExecutionResult()
        if res.status != Status.OK:
            result.Points = 0
            result.Status = res.status
            result.Time = res.time
            result.Memory = res.memory
            if res.status == Status.RE or res.status == Status.RV:
                result.Error = res.error
                if res.status == Status.RE:
                    result.ExitOnError = False
        else:
            try:
                correct, result.Points = self.check_output(test, output_path,
                                                           self.get_corresponding_test(test, exists=False))
                if correct:
                    result.Status = Status.OK
                else:
                    result.Status = Status.WA
                result.Time = res.time
                result.Memory = res.memory
            except CheckerOutputException as e:
                result.Status = Status.RE
                result.Error = e.message

        return result

    def run_solutions(self, compiled_commands: List[Tuple[Solution, bool]], solutions):
        """
        Run solutions on tests and print the results as a table to stdout.
        """
        executions: List[RunExecution] = []
        all_cache_files: Dict[str, CacheFile] = {}
        all_results = collections.defaultdict(
            lambda: collections.defaultdict(lambda: collections.defaultdict(ExecutionResult)))

        for (solution, result) in compiled_commands:
            lang = solution.lang
            solution_cache = solution.get_cache_file()
            all_cache_files[solution.basename] = solution_cache

            if result:
                for test in self.tests:
                    test_time_limit = package_util.get_time_limit(test, self.config, lang, self.task_id, self.args)
                    test_memory_limit = package_util.get_memory_limit(test, self.config, lang, self.task_id, self.args)

                    test_result: CacheTest = solution_cache.tests.get(self.test_md5sums[test.basename], None)
                    if test_result is not None and test_result.time_limit == test_time_limit and \
                            test_result.memory_limit == test_memory_limit and \
                            test_result.time_tool == self.timetool_manager.used_timetool.get_name():
                        all_results[solution.basename][test.group][test] = test_result.result
                    else:
                        executions.append(RunExecution(
                            solution=solution,
                            test=test,
                            time_limit=test_time_limit,
                            memory_limit=test_memory_limit,
                        ))
                        all_results[solution.basename][test.group][test] = ExecutionResult(Status.PENDING)
                os.makedirs(paths.get_executions_path(solution.basename), exist_ok=True)
            else:
                for test in self.tests:
                    all_results[solution.basename][test.group][test] = ExecutionResult(Status.CE)
        print()
        executions.sort(key=lambda e: (package_util.get_executable_key(e.solution), e.test.basename))
        program_groups_scores = collections.defaultdict(dict)
        print_data = PrintData(0)

        has_terminal, terminal_width, terminal_height = util.get_terminal_size()

        if has_terminal:
            run_event = threading.Event()
            run_event.set()
            thr = threading.Thread(target=printer.printer_thread,
                                   args=(
                                       run_event, print_view, self.task_id, program_groups_scores, all_results,
                                       print_data, solutions, executions, self.groups, self.scores, self.tests,
                                       self.possible_score, self.cpus, self.args.hide_memory, self.config, self.contest,
                                       self.args))
            thr.start()

        keyboard_interrupt = False
        with mp.Pool(self.cpus) as pool:
            try:
                for i, result in enumerate(pool.imap(self.run_solution, executions)):
                    execution = executions[i]
                    contest_points = self.contest.get_test_score(result, execution.time_limit, execution.memory_limit)
                    result.Points = contest_points
                    all_results[execution.solution.basename][execution.test.group][execution.test] = result
                    print_data.i = i

                    # We store the result in dictionary to write it to cache files later.
                    lang = execution.solution.lang
                    test_time_limit = package_util.get_time_limit(execution.test, self.config, lang, self.task_id,
                                                                  self.args)
                    test_memory_limit = package_util.get_memory_limit(execution.test, self.config, lang, self.task_id,
                                                                      self.args)
                    all_cache_files[execution.solution.basename].tests[execution.test.md5] = CacheTest(
                        time_limit=test_time_limit,
                        memory_limit=test_memory_limit,
                        time_tool=self.timetool_manager.used_timetool.get_name(),
                        result=result,
                    )
            except KeyboardInterrupt:
                keyboard_interrupt = True
            finally:
                if has_terminal:
                    run_event.clear()
                    thr.join()

        print("\n".join(
            print_view(terminal_width, terminal_height, self.task_id, program_groups_scores, all_results, print_data,
                       solutions, executions, self.groups, self.scores, self.tests, self.possible_score,
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
        os.makedirs(paths.get_executions_path(), exist_ok=True)
        compiled_commands = zip(solutions, compilation_results)
        return self.run_solutions(compiled_commands, solutions)

    def convert_status_to_string(self, dictionary):
        """
        Converts all `Status` enums in dict to strings.
        """
        def _convert(obj):
            if isinstance(obj, dict):
                return {k: _convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_convert(v) for v in obj]
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
        for test in InputTest.get_all(self.task_id):
            group = test.group
            if group not in group_sizes:
                group_sizes[group] = 0
            group_sizes[group] += 1

        run_group_sizes = {}
        for test in self.tests:
            group = test.group
            if group not in run_group_sizes:
                run_group_sizes[group] = 0
            run_group_sizes[group] += 1

        whole_groups = []
        for group in group_sizes.keys():
            if group in run_group_sizes and group_sizes[group] == run_group_sizes[group]:
                whole_groups.append(group)
        return whole_groups

    def validate_expected_scores(self, results):
        new_expected_scores = {}  # Expected scores based on results

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
        if self.args.tests is None and config_expected_scores:  # If no groups were specified, use all groups from config
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

        expected_scores = {}  # Expected scores from config with only solutions and groups that were run
        for solution in used_solutions:
            if solution in config_expected_scores.keys():
                expected_scores[solution] = {
                    "expected": {},
                    "points": 0
                }

                for group in used_groups:
                    if group in config_expected_scores[solution]["expected"]:
                        expected_scores[solution]["expected"][group] = config_expected_scores[solution]["expected"][
                            group]

                expected_scores[solution]["points"] = self.contest.get_global_score(
                    expected_scores[solution]["expected"],
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
                if field == '':  # Solutions were added
                    for solution in change:
                        added_solutions.add(solution[0])
                elif field[1] == "expected":  # Groups were added
                    for group in change:
                        added_groups.add(group[0])
            elif type == "remove":
                # We check whether a solution was removed only when sinol_make was run on all of them
                if field == '' and self.args.solutions == None and config_expected_scores:
                    for solution in change:
                        removed_solutions.add(solution[0])
                # We check whether a group was removed only when sinol_make was run on all of them
                elif field[1] == "expected" and self.args.tests is None and config_expected_scores:
                    for group in change:
                        removed_groups.add(group[0])
            elif type == "change":
                if field[1] == "expected":  # Results for at least one group has changed
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
                elif field[1] == "points":  # Points for at least one solution has changed
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
                    print(
                        util.warning("Solution %s passed group %d with status %s while it should pass with status %s." %
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
                print(util.info("Saved suggested expected scores description."))
            else:
                util.exit_with_error("Use flag --apply-suggestions to apply suggestions.")

    def validate_arguments(self, args):
        if args.time_tool is None and self.config.get('sinol_undocumented_time_tool', '') != '':
            args.time_tool = self.config['sinol_undocumented_time_tool']
        try:
            self.timetool_manager.set_timetool(args)
        except ValueError:
            util.exit_with_error('Invalid time tool specified.')

    def exit(self):
        if len(self.failed_compilations) > 0:
            util.exit_with_error('Compilation failed for {cnt} solution{letter}.'.format(
                cnt=len(self.failed_compilations), letter='' if len(self.failed_compilations) == 1 else 's'))

    def set_scores(self):
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

    def get_valid_input_files(self) -> List[InputTest]:
        """
        Returns list of input files that have corresponding output file.
        """
        outputs = OutputTest.get_all(self.task_id)
        output_tests_ids = [test.test_id for test in outputs]
        valid_input_files = []
        for test in self.tests:
            if test.test_id in output_tests_ids:
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
                [test.basename for test in missing_tests])))
            print(util.warning('Running only on tests with output files.'))
            self.tests: List[InputTest] = valid_input_files

    def check_are_any_tests_to_run(self):
        """
        Checks if there are any tests to run and prints them and checks
        if all input files have corresponding output files.
        """
        if len(self.tests) > 0:
            print(util.bold('Tests that will be run:'), ' '.join([test.basename for test in self.tests]))

            example_tests = [test for test in self.tests if test.group == 0]
            if len(example_tests) == len(self.tests):
                print(util.warning('Running only on example tests.'))

            if not self.has_lib:
                self.validate_existence_of_outputs()
            self.groups = self.get_groups(self.tests)
        else:
            util.exit_with_error('There are no tests to run.')

    def check_errors(self, results: Dict[str, Dict[str, Dict[InputTest, ExecutionResult]]]):
        """
        Checks if there were any errors during execution and exits if there were.
        :param results: Dictionary of results.
        :return:
        """
        error_msg = ""
        exit = False
        for solution in results:
            for group in results[solution]:
                for test in results[solution][group]:
                    if results[solution][group][test].Error is not None:
                        error_msg += (f'Solution {solution} had an error on test {test.basename}: '
                                      f'{results[solution][group][test].Error}\n')
                        exit |= results[solution][group][test].ExitOnError
        if error_msg != "":
            if exit:
                util.exit_with_error(error_msg)
            else:
                print(util.warning(error_msg))

    def run(self, args):
        super().run(args)
        package_util.validate_test_names(self.task_id)

        try:
            self.contest = contest_types.get_contest_type()
        except UnknownContestType as e:
            util.exit_with_error(str(e))

        if 'title' not in self.config.keys():
            util.exit_with_error('Title was not defined in config.yml.')
        self.validate_arguments(args)
        title = self.config["title"]
        print("Task: %s (tag: %s)" % (title, self.task_id))
        self.cpus = args.cpus or util.default_cpu_count()
        cache.save_to_cache_extra_compilation_files(self.config.get("extra_compilation_files", []), self.task_id)
        cache.remove_results_if_contest_type_changed(self.config.get("sinol_contest_type", "default"))

        if self.checker_exists():
            self.checker = self.get_checker()
            print(util.info(f"Checker found: {self.checker.basename}"))
            exe, compile_log = self.checker.compile()
            if exe is None:
                util.exit_with_error("Checker compilation failed.")
                self.compiler_manager.print_compile_log(compile_log)
        else:
            self.checker = None

        lib = package_util.get_files_matching_pattern(self.task_id, f'{self.task_id}lib.*')
        self.has_lib = len(lib) != 0

        self.tests: List[InputTest] = InputTest.get_all(self.task_id, arg_tests=args.tests)
        self.test_md5sums = {test.basename: test.md5 for test in self.tests}
        self.check_are_any_tests_to_run()
        self.set_scores()
        self.failed_compilations = []
        solutions = self.get_all_solutions(self.args.solutions)

        util.change_stack_size_to_unlimited()
        for solution in solutions:
            lang = solution.lang
            for test in self.tests:
                # These functions will exit if the limits are not set
                _ = package_util.get_time_limit(test, self.config, lang, self.task_id, self.args)
                _ = package_util.get_memory_limit(test, self.config, lang, self.task_id, self.args)

        results, all_results = self.compile_and_run(solutions)
        self.check_errors(all_results)
        try:
            validation_results = self.validate_expected_scores(results)
        except Exception:
            self.config = util.try_fix_config(self.config)
            try:
                validation_results = self.validate_expected_scores(results)
            except Exception:
                util.exit_with_error("Validating expected scores failed. "
                                     "This probably means that `sinol_expected_scores` is broken. "
                                     "Delete it and run `sinol-make run --apply-suggestions` again.")
        self.print_expected_scores_diff(validation_results)
        self.exit()
