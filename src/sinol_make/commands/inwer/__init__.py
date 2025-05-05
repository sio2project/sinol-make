import subprocess
import sys
import signal
import threading
import argparse
import os
import multiprocessing as mp
from functools import cmp_to_key
from typing import Dict, List

from sio3pack.test import Test

from sinol_make import util, contest_types
from sinol_make.structs.inwer_structs import TestResult, InwerExecution, VerificationResult, TableData
from sinol_make.helpers import package_util, printer, paths, parsers
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.commands.inwer import inwer_util


class Command(BaseCommand):
    """
    Class for "inwer" command.
    """

    def get_name(self):
        return "inwer"

    def get_short_name(self):
        return "i"

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
        parsers.add_cpus_argument(parser, 'number of cpus to use when verifying tests')
        parsers.add_fsanitize_argument(parser)
        parsers.add_compilation_arguments(parser)
        return parser

    @staticmethod
    def verify_test(execution: InwerExecution) -> VerificationResult:
        """
        Verifies a test and returns the result of inwer on this test.
        """
        output_dir = paths.get_executables_path(execution.test.test_name)
        os.makedirs(output_dir, exist_ok=True)

        command = [execution.inwer_exe_path, os.path.basename(execution.test.test_name)]
        with open(execution.test.in_file.path, 'r') as test:
            process = subprocess.Popen(command, stdin=test, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.wait()
        exit_code = process.returncode
        out, _ = process.communicate()

        return VerificationResult(
            execution.test,
            exit_code == 0,
            out.decode('utf-8')
        )

    def verify_and_print_table(self) -> Dict[Test, TestResult]:
        """
        Verifies all tests and prints the results in a table.
        :return: dictionary of TestResult objects
        """
        results = {}
        sorted_tests = sorted(self.tests, key=lambda test: test.group)
        executions: List[InwerExecution] = []
        for test in sorted_tests:
            results[test.test_name] = TestResult(test)
            executions.append(InwerExecution(test, self.inwer_executable))

        has_terminal, terminal_width, terminal_height = util.get_terminal_size()
        has_terminal = False

        table_data = TableData(results, 0)
        if has_terminal:
            run_event = threading.Event()
            run_event.set()
            thr = threading.Thread(target=printer.printer_thread, args=(run_event, inwer_util.print_view, table_data))
            thr.start()

        keyboard_interrupt = False
        sanitizer_error = False
        try:
            with mp.Pool(self.cpus) as pool:
                for i, result in enumerate(pool.imap(self.verify_test, executions)):
                    table_data.results[result.test.test_name].set_results(result.valid, result.output)
                    table_data.i = i
                    if util.has_sanitizer_error(result.output, 0 if result.valid else 1):
                        sanitizer_error = True
        except KeyboardInterrupt:
            keyboard_interrupt = True

        if has_terminal:
            run_event.clear()
            thr.join()

        print("\n".join(inwer_util.print_view(terminal_width, terminal_height, table_data)[0]))

        if sanitizer_error:
            print(util.warning('Warning: if inwer failed due to sanitizer errors, you can either run '
                               '`sudo sysctl vm.mmap_rnd_bits = 28` to fix this or disable sanitizers with the '
                               '--no-fsanitize flag.'))
        if keyboard_interrupt:
            util.exit_with_error('Keyboard interrupt.')

        return results

    def verify_tests_order(self):
        """
        Verifies if tests are in correct order.
        """

        ocen = sorted([test for test in self.tests if test.in_file.path.endswith('ocen.in')],
                      key=lambda test: test.test_id)
        tests = list(set(self.tests) - set(ocen))
        last_id = None
        last_test = None
        for test in ocen:
            test_id = int("".join(filter(str.isdigit, test.test_id)))
            if last_id is not None and test_id != last_id + 1:
                util.exit_with_error(f'Test {test.test_id} is in wrong order. '
                                     f'Last test was {last_test.test_id}.')
            last_id = test_id
            last_test = test

        def is_next(last, curr):
            if last == "" and curr != "a":
                return False
            elif last == "":
                return True
            i = len(last) - 1
            while i >= 0:
                if last[i] != 'z':
                    last = last[:i] + chr(ord(last[i]) + 1) + last[i + 1:]
                    break
                else:
                    last = last[:i] + 'a' + last[i + 1:]
                    i -= 1
                    if i < 0:
                        last = 'a' + last
            return last == curr

        def compare_id(test1: Test, test2: Test):
            id1 = test1.test_id
            id2 = test2.test_id
            if id1 == id2:
                return 0
            if len(id1) == len(id2):
                if id1 < id2:
                    return -1
                return 1
            elif len(id1) < len(id2):
                return -1
            return 1

        groups = {}
        for group in package_util.get_groups():
            groups[group] = sorted([test for test in tests if test.group == group],
                                   key=cmp_to_key(compare_id))
        for group, group_tests in groups.items():
            last_id = None
            last_test = None
            for test in group_tests:
                test_id = "".join([c for c in test.test_id if not c.isdigit()])
                if last_id is not None and not is_next(last_id, test_id):
                    util.exit_with_error(f'Test {test.test_id} is in wrong order. '
                                         f'Last test was {last_test.test_id}.')
                last_id = test_id
                last_test = test

    def run(self, args: argparse.Namespace):
        args = util.init_package_command(args)

        self.task_id = package_util.get_task_id()
        package_util.validate_test_names()
        self.inwer = inwer_util.get_inwer_path(args.inwer_path)
        if self.inwer is None:
            if args.inwer_path is None:
                util.exit_with_error('No inwer found in `prog/` directory.')
            else:
                util.exit_with_error(f'Inwer "{args.inwer_path}" not found.')
        relative_path = os.path.relpath(self.inwer, os.getcwd())
        print(f'Verifying with inwer {util.bold(relative_path)}')

        self.cpus = args.cpus or util.default_cpu_count()
        self.tests = package_util.get_tests(args.tests)
        self.contest_type = contest_types.get_contest_type()

        if len(self.tests) == 0:
            util.exit_with_error('No tests found.')
        else:
            print('Verifying tests: ' + util.bold(', '.join([test.test_id for test in self.tests])))

        util.change_stack_size_to_unlimited()
        self.inwer_executable = inwer_util.compile_inwer(self.inwer, args, args.compile_mode, args.fsanitize)
        results: Dict[Test, TestResult] = self.verify_and_print_table()
        print('')

        failed_tests = []
        for result in results.values():
            if not result.valid:
                failed_tests.append(result.test.test_name)

        if len(failed_tests) > 0:
            util.exit_with_error(f'Verification failed for tests: {", ".join(failed_tests)}')
        elif self.contest_type.verify_tests_order():
            print("Verifying tests order...")
            self.verify_tests_order()
        print(util.info('Verification successful.'))
