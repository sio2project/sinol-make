import argparse

from sinol_make import util
from sinol_make.commands.ingen import Command as IngenCommand
from sinol_make.commands.outgen import Command as OutgenCommand
from sinol_make.helpers import parsers, package_util
from sinol_make.interfaces.BaseCommand import BaseCommand


class Command(BaseCommand):
    """
    Class for `gen` command.
    """

    def get_name(self):
        return "gen"

    def get_short_name(self):
        return "g"

    def configure_subparser(self, subparser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Generate input and output files',
            description='Generate input files using ingen program '
                        '(for example prog/abcingen.cpp for abc task). Whenever '
                        'the new input differs from the previous one, '
                        'the model solution will be used to generate the new output '
                        'file. You can also specify your ingen source '
                        'file which will be used.'
        )

        parser.add_argument('ingen_path', type=str, nargs='?',
                            help='path to ingen source file, for example prog/abcingen.cpp')
        parser.add_argument('-i', '--only-inputs', action='store_true', help='generate input files only')
        parser.add_argument('-o', '--only-outputs', action='store_true', help='generate output files only')
        parsers.add_cpus_argument(parser, 'number of cpus to use to generate output files')
        parser.add_argument('-n', '--no-validate', default=False, action='store_true',
                            help='do not validate test contents')
        parsers.add_fsanitize_argument(parser)
        parsers.add_compilation_arguments(parser)
        return parser

    def run(self, args: argparse.Namespace):
        args = util.init_package_command(args)

        self.args = args
        self.ins = args.only_inputs
        self.outs = args.only_outputs
        self.task_type = package_util.get_task_type_cls()
        # If no arguments are specified, generate both input and output files.
        if not self.ins and not self.outs:
            self.ins = True
            self.outs = True

        if self.ins:
            command = IngenCommand()
            command.run(args)

        if not self.task_type.run_outgen():
            print(util.warning("Outgen is not supported for this task type."))
            return

        if self.outs:
            command = OutgenCommand()
            command.run(args)
