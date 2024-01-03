import argparse
import os

from sinol_make import util
from sinol_make.commands.ingen.ingen_util import get_ingen, compile_ingen, run_ingen
from sinol_make.helpers import parsers, package_util
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
        parsers.add_compilation_arguments(parser)

    def run(self, args: argparse.Namespace):
        util.exit_if_not_package()

        self.args = args

        self.task_id = package_util.get_task_id()
        package_util.validate_test_names(self.task_id)
        util.change_stack_size_to_unlimited()
        self.ingen = get_ingen(self.task_id, args.ingen_path)
        print(util.info(f'Using ingen file {os.path.basename(self.ingen)}'))
        self.ingen_exe = compile_ingen(self.ingen, self.args, self.args.weak_compilation_flags)

        if run_ingen(self.ingen_exe):
            print(util.info('Successfully generated input files.'))
        else:
            util.exit_with_error('Failed to generate input files.')
