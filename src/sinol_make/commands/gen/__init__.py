import argparse
import glob
import os
import yaml

import multiprocessing as mp

from sinol_make import util
from sinol_make.commands.gen import gen_util
from sinol_make.structs.gen_structs import OutputGenerationArguments
from sinol_make.helpers import parsers, package_util
from sinol_make.interfaces.BaseCommand import BaseCommand


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
        parser.add_argument('-c', '--cpus', type=int,
                            help=f'number of cpus to use to generate output files (default: {mp.cpu_count()} - all available)',
                            default=mp.cpu_count())
        parsers.add_compilation_arguments(parser)

    def generate_outputs(self, outputs_to_generate):
        print(f'Generating output files for {len(outputs_to_generate)} tests on {self.args.cpus} cpus.')
        arguments = []
        for output in outputs_to_generate:
            output_basename = os.path.basename(output)
            input = os.path.join(os.getcwd(), 'in', os.path.splitext(output_basename)[0] + '.in')
            arguments.append(OutputGenerationArguments(self.correct_solution_exe, input, output))

        with mp.Pool(self.args.cpus) as pool:
            results = []
            for i, result in enumerate(pool.imap(gen_util.generate_output, arguments)):
                results.append(result)
                if result:
                    print(util.info(f'Successfully generated output file {os.path.basename(arguments[i].output_test)}'))
                else:
                    print(util.error(f'Failed to generate output file {os.path.basename(arguments[i].output_test)}'))

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
        outputs_to_generate = []
        for file in glob.glob(os.path.join(os.getcwd(), 'in', '*.in')):
            basename = os.path.basename(file)
            md5_sums[basename] = util.get_file_md5(file)

            if old_md5_sums is None or old_md5_sums.get(basename, '') != md5_sums[basename]:
                output_basename = os.path.splitext(os.path.basename(basename))[0] + '.out'
                outputs_to_generate.append(os.path.join(os.getcwd(), "out", output_basename))

        return md5_sums, outputs_to_generate

    def run(self, args: argparse.Namespace):
        util.exit_if_not_package()

        self.args = args
        self.task_id = package_util.get_task_id()
        package_util.validate_test_names(self.task_id)
        self.ingen = gen_util.get_ingen(self.task_id, args.ingen_path)
        print(util.info(f'Using ingen file {os.path.basename(self.ingen)}'))

        self.correct_solution = gen_util.get_correct_solution(self.task_id)
        self.ingen_exe = gen_util.compile_ingen(self.ingen, self.args, self.args.weak_compilation_flags)

        util.change_stack_size_to_unlimited()
        if gen_util.run_ingen(self.ingen_exe):
            print(util.info('Successfully generated input files.'))
        else:
            util.exit_with_error('Failed to generate input files.')
        md5_sums, outputs_to_generate = self.calculate_md5_sums()
        if len(outputs_to_generate) == 0:
            print(util.info('All output files are up to date.'))
        else:
            self.correct_solution_exe = gen_util.compile_correct_solution(self.correct_solution, self.args,
                                                                          self.args.weak_compilation_flags)
            self.generate_outputs(outputs_to_generate)

        with open(os.path.join(os.getcwd(), 'in', '.md5sums'), 'w') as f:
            yaml.dump(md5_sums, f)
