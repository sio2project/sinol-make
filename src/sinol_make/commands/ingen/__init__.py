import argparse
import glob
import os

from sinol_make import util
from sinol_make.commands.ingen.ingen_util import get_ingen, compile_ingen, run_ingen
from sinol_make.helpers import parsers, package_util, paths
from sinol_make.interfaces.BaseCommand import BaseCommand


class Command(BaseCommand):
    """
    Class for `ingen` command.
    """

    def get_name(self):
        return "ingen"

    def configure_subparser(self, subparser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Generate input files',
            description='Generate input files using ingen program '
                        '(for example prog/abcingen.cpp for abc task).'
                        'You can also specify your ingen source '
                        'file which will be used.'
        )

        parser.add_argument('ingen_path', type=str, nargs='?',
                            help='path to ingen source file, for example prog/abcingen.cpp')
        parser.add_argument('-n', '--no-validate', default=False, action='store_true',
                            help='do not validate test contents')
        parsers.add_compilation_arguments(parser)

    def run(self, args: argparse.Namespace):
        args = util.init_package_command(args)

        self.args = args

        self.task_id = package_util.get_task_id()
        package_util.validate_test_names(self.task_id)
        util.change_stack_size_to_unlimited()
        self.ingen = get_ingen(self.task_id, args.ingen_path)
        print(util.info(f'Using ingen file {os.path.basename(self.ingen)}'))
        self.ingen_exe = compile_ingen(self.ingen, self.args, self.args.compile_mode)

        previous_tests = []
        try:
            with open(paths.get_cache_path("input_tests"), "r") as f:
                for line in f:
                    line = line.strip()
                    if os.path.exists(line):
                        previous_tests.append(line)
        except FileNotFoundError:
            pass
        dates = {os.path.basename(test): os.path.getmtime(test) for test in previous_tests}

        if run_ingen(self.ingen_exe):
            print(util.info('Successfully generated input files.'))
        else:
            util.exit_with_error('Failed to generate input files.')

        print(util.info('Cleaning up old input files.'))
        for test in glob.glob(os.path.join(os.getcwd(), "in", f"{self.task_id}*.in")):
            basename = os.path.basename(test)
            if basename in dates and dates[basename] == os.path.getmtime(test):
                os.unlink(test)

        with open(paths.get_cache_path("input_tests"), "w") as f:
            f.write("\n".join(glob.glob(os.path.join(os.getcwd(), "in", f"{self.task_id}*.in"))))

        if not self.args.no_validate:
            print(util.info('Validating input test contents.'))
            tests = sorted(glob.glob(os.path.join(os.getcwd(), "in", f"{self.task_id}*.in")))
            for test in tests:
                package_util.validate_test(test)
            print(util.info('Input test contents are valid!'))
