import subprocess
import sys
import signal
import threading
import argparse
import os
import multiprocessing as mp
from typing import Dict, List

from sinol_make import util
from sinol_make.structs.inwer_structs import TestResult, InwerExecution, VerificationResult, TableData
from sinol_make.helpers import package_util, compile, printer, paths
from sinol_make.helpers.parsers import add_compilation_arguments
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.commands.inwer import inwer_util


class Command(BaseCommand):
    """
    Class for "inwer" command.
    """

    def get_name(self):
        return "inwer"

    def configure_subparser(self, subparser: argparse.ArgumentParser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Verify if input files are correct',
            description='Verify if input files are correct using inwer program '
                        '(for example prog/abcinwer.cpp for abc task). You can also '
                        'specify your inwer source file which will be used.'
        )

        parser.add_argument('inwer_path', type=str, nargs='?',
                            help='path to inwer source file, for example prog/abcinwer.cpp')
        parser.add_argument('-t', '--tests', type=str, nargs='+',
                            help='test to verify, for example in/abc{0,1}*')
        parser.add_argument('-c', '--cpus', type=int,
                            help=f'number of cpus to use (default: {mp.cpu_count()} -all available)')
        add_compilation_arguments(parser)

    def compile_inwer(self, args: argparse.Namespace):
        self.inwer_executable, compile_log_path = inwer_util.compile_inwer(self.inwer, args, args.weak_compilation_flags)
        if self.inwer_executable is None:
            util.exit_with_error('Compilation failed.', lambda: compile.print_compile_log(compile_log_path))
        else:
            print(util.info('Compilation successful.'))

    @staticmethod
    def verify_test(execution: InwerExecution) -> VerificationResult:
        """
        Verifies a test and returns the result of inwer on this test.
        """
        output_dir = paths.get_executables_path(execution.test_name)
        os.makedirs(output_dir, exist_ok=True)

        command = [execution.inwer_exe_path]
        with open(execution.test_path, 'r') as test:
            process = subprocess.Popen(command, stdin=test, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       preexec_fn=os.setsid)

            def sigint_handler(signum, frame):
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
                sys.exit(1)
            signal.signal(signal.SIGINT, sigint_handler)

            process.wait()
        exit_code = process.returncode
        out, _ = process.communicate()

        return VerificationResult(
            execution.test_path,
            exit_code == 0,
            out.decode('utf-8')
        )

    def verify_and_print_table(self) -> Dict[str, TestResult]:
        """
        Verifies all tests and prints the results in a table.
        :return: dictionary of TestResult objects
        """
        results = {}
        sorted_tests = sorted(self.tests, key=lambda test: package_util.get_group(test, self.task_id))
        executions: List[InwerExecution] = []
        for test in sorted_tests:
            results[test] = TestResult(test, self.task_id)
            executions.append(InwerExecution(test, results[test].test_name, self.inwer_executable))

        has_terminal, terminal_width, terminal_height = util.get_terminal_size()

        table_data = TableData(results, 0, self.task_id)
        if has_terminal:
            run_event = threading.Event()
            run_event.set()
            thr = threading.Thread(target=printer.printer_thread, args=(run_event, inwer_util.print_view, table_data))
            thr.start()

        keyboard_interrupt = False
        try:
            with mp.Pool(self.cpus) as pool:
                for i, result in enumerate(pool.imap(self.verify_test, executions)):
                    table_data.results[result.test_path].set_results(result.valid, result.output)
                    table_data.i = i
        except KeyboardInterrupt:
            keyboard_interrupt = True

        if has_terminal:
            run_event.clear()
            thr.join()

        print("\n".join(inwer_util.print_view(terminal_width, terminal_height, table_data)[0]))

        if keyboard_interrupt:
            util.exit_with_error('Keyboard interrupt.')

        return results

    def run(self, args: argparse.Namespace):
        util.exit_if_not_package()

        self.task_id = package_util.get_task_id()
        package_util.validate_test_names(self.task_id)
        self.inwer = inwer_util.get_inwer_path(self.task_id, args.inwer_path)
        if self.inwer is None:
            if args.inwer_path is None:
                util.exit_with_error('No inwer found in `prog/` directory.')
            else:
                util.exit_with_error(f'Inwer "{args.inwer_path}" not found.')
        relative_path = os.path.relpath(self.inwer, os.getcwd())
        print(f'Verifying with inwer {util.bold(relative_path)}')

        self.cpus = args.cpus or mp.cpu_count()
        self.tests = package_util.get_tests(self.task_id, args.tests)

        if len(self.tests) == 0:
            util.exit_with_error('No tests found.')
        else:
            print('Verifying tests: ' + util.bold(', '.join(self.tests)))

        util.change_stack_size_to_unlimited()
        self.compile_inwer(args)
        results: Dict[str, TestResult] = self.verify_and_print_table()
        print('')

        failed_tests = []
        for result in results.values():
            if not result.valid:
                failed_tests.append(result.test_name)

        if len(failed_tests) > 0:
            util.exit_with_error(f'Verification failed for tests: {", ".join(failed_tests)}')
        else:
            print(util.info('Verification successful.'))
            exit(0)
