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
        parsers.add_cpus_argument(parser, 'number of cpus used for validating tests')
        parsers.add_fsanitize_argument(parser)
        parsers.add_compilation_arguments(parser)
        return parser

    def delete_dangling_files(self, dates):
        to_delete = set()
        for test in glob.glob(os.path.join(os.getcwd(), "in", f"{self.task_id}*.in")):
            basename = os.path.basename(test)
            if basename in dates and dates[basename] == os.path.getmtime(test):
                to_delete.add(os.path.basename(test))
        if to_delete:
            config = package_util.get_config()
            if 'sinol_static_tests' not in config:
                print(util.warning('Old input files won\'t be deleted, '
                                   'because static tests are not defined. '
                                   'You can define them in config.yml with `sinol_static_tests` key.'))
            else:
                static_files = config['sinol_static_tests']
                if isinstance(static_files, str):
                    static_files = [static_files]
                static_files = set([os.path.basename(test) for test in static_files])
                to_delete = to_delete - static_files
                if to_delete:
                    print('Cleaning up old input files.')
                    for test in to_delete:
                        os.remove(os.path.join(os.getcwd(), "in", test))

    def run(self, args: argparse.Namespace):
        args = util.init_package_command(args)

        self.args = args

        self.task_id = package_util.get_task_id()
        util.change_stack_size_to_unlimited()
        self.ingen = get_ingen(self.task_id, args.ingen_path)
        print(f'Using ingen file {os.path.basename(self.ingen)}')
        self.ingen_exe = compile_ingen(self.ingen, self.args, self.args.compile_mode, self.args.fsanitize)

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

        self.delete_dangling_files(dates)

        with open(paths.get_cache_path("input_tests"), "w") as f:
            f.write("\n".join(glob.glob(os.path.join(os.getcwd(), "in", f"{self.task_id}*.in"))))

        if not self.args.no_validate:
            tests = sorted(glob.glob(os.path.join(os.getcwd(), "in", f"{self.task_id}*.in")))
            package_util.validate_tests(tests, self.args.cpus, 'input')
