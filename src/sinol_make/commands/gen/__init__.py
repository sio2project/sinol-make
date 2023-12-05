from typing import List, Tuple

import argparse
import glob
import os
import yaml

import multiprocessing as mp

from sinol_make import util
from sinol_make.commands.gen import gen_util
from sinol_make.structs.gen_structs import OutputGenerationArguments
from sinol_make.helpers import parsers, package_util, cache
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest


class Command(BaseCommand):
    """
    Class for `gen` command.
    """

    def get_name(self):
        return "gen"

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
        parser.add_argument('-c', '--cpus', type=int,
                            help=f'number of cpus to use to generate output files '
                                 f'(default: {util.default_cpu_count()})',
                            default=util.default_cpu_count())
        parsers.add_compilation_arguments(parser)

    def generate_outputs(self, outputs_to_generate: List[Tuple[OutputTest, InputTest]]):
        print(f'Generating output files for {len(outputs_to_generate)} tests on {self.args.cpus} cpus.')
        arguments = []
        for output, input in outputs_to_generate:
            arguments.append(OutputGenerationArguments(self.correct_solution, input, output))

        with mp.Pool(self.args.cpus) as pool:
            results = []
            for i, result in enumerate(pool.imap(gen_util.generate_output, arguments)):
                results.append(result)
                if result:
                    print(util.info(f'Successfully generated output file '
                                    f'{os.path.basename(arguments[i].output_test.basename)}'))
                else:
                    print(util.error(f'Failed to generate output file '
                                     f'{os.path.basename(arguments[i].output_test.basename)}'))

            if not all(results):
                util.exit_with_error('Failed to generate some output files.')
            else:
                print(util.info('Successfully generated all output files.'))

    def calculate_md5_sums(self):
        """
        Calculates md5 sums for each test.
        :return: Tuple (dictionary of md5 sums, list of outputs tests that need to be generated)
        """
        old_md5_sums = None
        try:
            with open(os.path.join(os.getcwd(), 'in', '.md5sums'), 'r') as f:
                file_content = yaml.load(f, Loader=yaml.FullLoader)
                if isinstance(file_content, dict):
                    old_md5_sums = file_content
        except (yaml.YAMLError, OSError):
            pass

        md5_sums = {}
        outputs_to_generate: List[Tuple[OutputTest, InputTest]] = []
        for input in InputTest.get_all(self.task_id):
            output = self.get_corresponding_test(input, exists=False)
            md5_sums[input.basename] = input.md5

            if old_md5_sums is None or old_md5_sums.get(input.basename, '') != md5_sums[input.basename]:
                outputs_to_generate.append((output, input))
            elif not os.path.exists(output.file_path):
                # If output file does not exist, generate it.
                outputs_to_generate.append((output, input))

        return md5_sums, outputs_to_generate

    def run(self, args: argparse.Namespace):
        super().run(args)

        self.ins = args.only_inputs
        self.outs = args.only_outputs
        # If no arguments are specified, generate both input and output files.
        if not self.ins and not self.outs:
            self.ins = True
            self.outs = True

        package_util.validate_test_names(self.task_id)
        util.change_stack_size_to_unlimited()
        cache.check_correct_solution(self.task_id)
        if self.ins:
            ingen = self.get_ingen(args.ingen_path)
            print(util.info(f'Using ingen file {ingen.basename}'))
            ingen.compile()

            if ingen.run():
                print(util.info('Successfully generated input files.'))
            else:
                util.exit_with_error('Failed to generate input files.')

        if self.outs:
            self.correct_solution = self.get_correct_solution()

            md5_sums, outputs_to_generate = self.calculate_md5_sums()
            if len(outputs_to_generate) == 0:
                print(util.info('All output files are up to date.'))
            else:
                self.correct_solution.compile()
                self.generate_outputs(outputs_to_generate)
                with open(os.path.join(os.getcwd(), 'in', '.md5sums'), 'w') as f:
                    yaml.dump(md5_sums, f)
