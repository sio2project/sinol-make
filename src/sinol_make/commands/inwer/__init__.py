import subprocess
import argparse
import os
import multiprocessing as mp

from sinol_make import util
from sinol_make.commands.inwer.structs import TestResult, InwerExecution, VerificationResult, TableData
from sinol_make.helpers import package_util, compile
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
                        '(for example prog/abcinwer.cpp for abc task).'
        )

        parser.add_argument('inwer_path', type=str, nargs='?',
                            help='path to inwer source file, for example prog/abcinwer.cpp')
        parser.add_argument('--tests', type=str, nargs='+',
                            help='test to verify, for example in/abc{0,1}*')
        parser.add_argument('--cpus', type=int,
                            help=f'number of cpus to use, by default {mp.cpu_count()} (all available)')
        add_compilation_arguments(parser)

    def compile_inwer(self, args: argparse.Namespace):
        self.inwer_executable, compile_log_path = inwer_util.compile_inwer(self.inwer, args)
        if self.inwer_executable is None:
            print(util.error('Compilation failed.'))
            compile.print_compile_log(compile_log_path)
            exit(1)
        else:
            print(util.info('Compilation successful.'))

    def verify_test(self, execution: InwerExecution) -> VerificationResult:
        """
        Verifies a test and returns the result of inwer on this test.
        """
        output_dir = os.path.join(os.getcwd(), 'cache', 'executions', execution.test_name)
        os.makedirs(output_dir, exist_ok=True)

        command = f'{execution.inwer_exe_path} < {execution.test_path}'
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.wait()
        exit_code = process.returncode
        out, _ = process.communicate()

        return VerificationResult(
            execution.test_path,
            exit_code == 0,
            out.decode('utf-8')
        )

    def verify_and_print_table(self) -> dict[str, TestResult]:
        results = {}
        sorted_tests = sorted(self.tests, key=lambda x: x[0])
        executions: list[InwerExecution] = []
        for test in sorted_tests:
            results[test] = TestResult(test)
            executions.append(InwerExecution(test, results[test].test_name, self.inwer_executable))

        table_data = TableData(results, 0)
        print('Verifying tests...\n\n')
        with mp.Pool(self.cpus) as pool:
            for i, result in enumerate(pool.imap(self.verify_test, executions)):
                table_data.results[result.test_path].set_results(result.valid, result.output)
                inwer_util.print_view(table_data)

        return results

    def run(self, args: argparse.Namespace):
        if not util.check_if_project():
            util.exit_with_error('You are not in a project directory (couldn\'t find config.yml in current directory).')

        self.task_id = package_util.get_task_id()
        self.inwer = inwer_util.get_inwer_path(self.task_id, args.inwer_path)
        if self.inwer is None:
            if args.inwer_path is None:
                util.exit_with_error('No inwer found in `prog/` directory.')
            else:
                util.exit_with_error(f'Inwer "{args.inwer_path}" not found.')
        relative_path = os.path.relpath(self.inwer, os.getcwd())
        print(f'Verifying with inwer {util.bold(relative_path)}')

        self.cpus = args.cpus or mp.cpu_count()
        self.tests = package_util.get_tests(args.tests)

        if len(self.tests) == 0:
            util.exit_with_error('No tests found.')
        else:
            print('Verifying tests: ' + util.bold(', '.join(self.tests)))

        self.compile_inwer(args)
        results: dict[str, TestResult] = self.verify_and_print_table()
        print('')

        failed_tests = []
        for result in results.values():
            if not result.valid:
                failed_tests.append(result.test_name)

        if len(failed_tests) > 0:
            util.exit_with_error(f'Verification failed for tests: {", ".join(failed_tests)}')
        else:
            print(util.info('Verification successful.'))
