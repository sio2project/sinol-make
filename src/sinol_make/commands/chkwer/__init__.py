import os
import subprocess
import threading
from typing import Dict, List
import multiprocessing as mp

from sinol_make import util, contest_types
from sinol_make.commands.chkwer import chkwer_util
from sinol_make.commands.outgen import outgen_util
from sinol_make.helpers import package_util, parsers, compiler, compile, printer, paths
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.structs.chkwer_structs import TestResult, ChkwerExecution, TableData, RunResult


class Command(BaseCommand):
    """
    Class for `chkwer` command.
    """

    def get_name(self):
        return "chkwer"

    def get_short_name(self):
        return "c"

    def configure_subparser(self, subparser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Run checker with model solution and print results',
            description='Run checker with model solution and print results. '
                        'Prints a table with points and checker\'s comments. '
                        'This command fails if the model solution didn\'t '
                        'score maximum points.'
        )
        parser.add_argument('-t', '--tests', type=str, nargs='+',
                            help='test to run, for example in/abc{0,1}*')
        parsers.add_cpus_argument(parser, 'number of cpus to use when verifying tests')
        parsers.add_compilation_arguments(parser)
        return parser

    def compile(self, file_path, exe_path, args, name, compilation_flags):
        print(f'Compiling {name}... ', end='')
        compilers = compiler.verify_compilers(args, [file_path])
        exe, compile_log_path = compile.compile_file(file_path, exe_path, compilers, compilation_flags,
                                                     use_fsanitize=False, use_extras=False)
        if exe is None:
            print(util.error('ERROR'))
            compile.print_compile_log(compile_log_path)
            util.exit_with_error(f'Failed {name} compilation.')
        else:
            print(util.info('OK'))
        return exe

    def run_test(self, execution: ChkwerExecution) -> RunResult:
        """
        Verifies a test and returns the result of chkwer on this test.
        """
        output_file = paths.get_chkwer_path(os.path.basename(execution.out_test_path))
        with open(execution.in_test_path, 'r') as inf, open(output_file, 'w') as outf:
            process = subprocess.Popen([execution.model_exe], stdin=inf, stdout=outf)
            process.wait()
        ok, points, comment = self.task_type.check_output(execution.in_test_path, output_file, execution.out_test_path)

        return RunResult(execution.in_test_path, ok, int(points), comment)

    def run_and_print_table(self) -> Dict[str, TestResult]:
        results = {}
        sorted_tests = sorted(self.tests, key=lambda test: package_util.get_group(test, self.task_id))
        executions: List[ChkwerExecution] = []
        for test in sorted_tests:
            results[test] = TestResult(test, self.task_id)
            executions.append(ChkwerExecution(test, results[test].test_name, package_util.get_out_from_in(test),
                                              self.checker_executable, self.model_executable))

        has_terminal, terminal_width, terminal_height = util.get_terminal_size()
        table_data = TableData(results, 0, self.task_id, self.contest_type.max_score_per_test())
        if has_terminal:
            run_event = threading.Event()
            run_event.set()
            thr = threading.Thread(target=printer.printer_thread, args=(run_event, chkwer_util.print_view, table_data))
            thr.start()

        keyboard_interrupt = False
        try:
            with mp.Pool(self.cpus) as pool:
                for i, result in enumerate(pool.imap(self.run_test, executions)):
                    table_data.results[result.test_path].set_results(result.points, result.ok, result.comment)
                    table_data.i = i
        except KeyboardInterrupt:
            keyboard_interrupt = True

        if has_terminal:
            run_event.clear()
            thr.join()

        print("\n".join(chkwer_util.print_view(terminal_width, terminal_height, table_data)[0]))
        if keyboard_interrupt:
            util.exit_with_error("Keyboard interrupt.")
        return results

    def run(self, args):
        args = util.init_package_command(args)
        self.task_id = package_util.get_task_id()
        self.task_type = package_util.get_task_type("time", None)
        self.contest_type = contest_types.get_contest_type()

        if self.task_type.name() != "normal":
            util.exit_with_error("chkwer can be run only for normal tasks.")

        self.cpus = args.cpus or util.default_cpu_count()
        self.tests = package_util.get_tests(self.task_id, args.tests)

        if len(self.tests) == 0:
            util.exit_with_error("No tests found.")
        else:
            print('Will run on tests: ' + util.bold(', '.join(self.tests)))
        util.change_stack_size_to_unlimited()

        additional_files = self.task_type.additional_files_to_compile()
        if len(additional_files) == 0:
            util.exit_with_error("Checker not found.")
        if len(additional_files) != 1:
            util.exit_with_error("More than one file to compile found. How is that possible?")
        checker_info = additional_files[0]
        model_solution = outgen_util.get_correct_solution(self.task_id)
        self.checker_executable = self.compile(checker_info[0], checker_info[1], args, "checker",
                                               args.compile_mode)
        self.model_executable = self.compile(model_solution, package_util.get_executable(model_solution), args,
                                             "model solution", args.compile_mode)
        print()

        results = self.run_and_print_table()
        for result in results.values():
            if not result.ok or result.points != self.contest_type.max_score_per_test():
                util.exit_with_error("Model solution didn't score maximum points.")
        print(util.info("Checker verification successful."))
