import argparse
import glob
import os
import yaml

import multiprocessing as mp

from sinol_make import util
from sinol_make.commands.outgen.outgen_util import get_correct_solution, compile_correct_solution, generate_output
from sinol_make.structs.gen_structs import OutputGenerationArguments
from sinol_make.helpers import parsers, package_util, cache
from sinol_make.interfaces.BaseCommand import BaseCommand


class Command(BaseCommand):
    """
    Class for `gen` command.
    """

    def get_name(self):
        return "outgen"

    def configure_subparser(self, subparser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Generate output files',
            description='Generate output files using the correct solution.'
        )

        parser.add_argument('-c', '--cpus', type=int,
                            help=f'number of cpus to use to generate output files '
                                 f'(default: {util.default_cpu_count()})',
                            default=util.default_cpu_count())
        parsers.add_compilation_arguments(parser)

    def generate_outputs(self, outputs_to_generate):
        print(f'Generating output files for {len(outputs_to_generate)} tests on {self.args.cpus} cpus.')
        arguments = []
        for output in outputs_to_generate:
            output_basename = os.path.basename(output)
            in_dir = os.path.join("/", *(os.path.abspath(output).split(os.sep)[:-2]), 'in')
            input = os.path.join(in_dir, os.path.splitext(output_basename)[0] + '.in')
            arguments.append(OutputGenerationArguments(self.correct_solution_exe, input, output))

        with mp.Pool(self.args.cpus) as pool:
            results = []
            for i, result in enumerate(pool.imap(generate_output, arguments)):
                results.append(result)
                if result:
                    print(util.info(f'Successfully generated output file {os.path.basename(arguments[i].output_test)}'))
                else:
                    print(util.error(f'Failed to generate output file {os.path.basename(arguments[i].output_test)}'))

            if not all(results):
                util.exit_with_error('Failed to generate some output files.')
            else:
                print(util.info('Successfully generated all output files.'))

    def calculate_md5_sums(self, tests=None):
        """
        Calculates md5 sums for each test.
        :return: Tuple (dictionary of md5 sums, list of outputs tests that need to be generated)
        """
        if tests is None:
            tests = glob.glob(os.path.join(os.getcwd(), 'in', '*.in'))

        old_md5_sums = None
        try:
            with open(os.path.join(os.getcwd(), 'in', '.md5sums'), 'r') as f:
                file_content = yaml.load(f, Loader=yaml.FullLoader)
                if isinstance(file_content, dict):
                    old_md5_sums = file_content
        except (yaml.YAMLError, OSError):
            pass

        md5_sums = {}
        outputs_to_generate = []
        for file in tests:
            basename = os.path.basename(file)
            output_basename = os.path.splitext(os.path.basename(basename))[0] + '.out'
            output_path = os.path.join(os.getcwd(), 'out', output_basename)
            md5_sums[basename] = util.get_file_md5(file)

            if old_md5_sums is None or old_md5_sums.get(basename, '') != md5_sums[basename]:
                outputs_to_generate.append(output_path)
            elif not os.path.exists(output_path):
                # If output file does not exist, generate it.
                outputs_to_generate.append(output_path)

        return md5_sums, outputs_to_generate

    def run(self, args: argparse.Namespace):
        util.exit_if_not_package()

        self.args = args
        self.task_id = package_util.get_task_id()
        package_util.validate_test_names(self.task_id)
        util.change_stack_size_to_unlimited()
        cache.check_correct_solution(self.task_id)
        self.correct_solution = get_correct_solution(self.task_id)

        md5_sums, outputs_to_generate = self.calculate_md5_sums()
        if len(outputs_to_generate) == 0:
            print(util.info('All output files are up to date.'))
        else:
            self.correct_solution_exe = compile_correct_solution(self.correct_solution, self.args,
                                                                 self.args.weak_compilation_flags)
            self.generate_outputs(outputs_to_generate)
            with open(os.path.join(os.getcwd(), 'in', '.md5sums'), 'w') as f:
                yaml.dump(md5_sums, f)
