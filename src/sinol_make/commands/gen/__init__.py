import argparse
import glob
import os
import subprocess
import hashlib
import yaml

import multiprocessing as mp

from sinol_make import util
from sinol_make.commands.gen import gen_util
from sinol_make.commands.gen.structs import OutputGenerationArguments
from sinol_make.helpers import parsers, package_util, compile
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
            description='Generate input files using gingen program '
                        '(for example prog/abcingen.cpp for abc task). If there '
                        'is a new test or it differs from the previous one, '
                        'then the output file will be generated using the '
                        'correct solution. You can also specify your ingen source '
                        'file which will be used.'
        )

        parser.add_argument('ingen_path', type=str, nargs='?',
                            help='path to ingen source file, for example prog/abcingen.cpp')
        parser.add_argument('-c', '--cpus', type=int,
                            help=f'number of cpus to use, by default {mp.cpu_count()} (all available). '
                                 f'Used when generating output files.')
        parsers.add_compilation_arguments(parser)

    def compile_ingen(self):
        self.ingen_exe, compile_log_path = gen_util.compile_ingen(self.ingen, self.args)
        if self.ingen_exe is None:
            print(util.error('Failed ingen compilation.'))
            compile.print_compile_log(compile_log_path)
            exit(1)
        else:
            print(util.info('Successfully compiled ingen.'))

    def compile_correct_solution(self):
        self.correct_solution_exe, compile_log_path = gen_util.compile_correct_solution(self.correct_solution, self.args)
        if self.correct_solution_exe is None:
            print(util.error('Failed ingen compilation.'))
            compile.print_compile_log(compile_log_path)
            exit(1)
        else:
            print(util.info('Successfully compiled ingen.'))

    def generate_outputs(self, outputs_to_generate):
        arguments = []
        for output in outputs_to_generate:
            output_basename = os.path.basename(output)
            input = os.path.join(os.getcwd(), 'in', output_basename + '.in')
            arguments.append(OutputGenerationArguments(self.correct_solution_exe, input, output))

        failed = False
        with mp.Pool(self.args.cpus) as pool:
            for i, result in enumerate(pool.imap_unordered(gen_util.generate_output, arguments)):
                if result:
                    print(util.info(f'Successfully generated output file {os.path.basename(arguments[i].output_file)}'))
                else:
                    failed = True
                    print(util.error(f'Failed to generate output file {os.path.basename(arguments[i].output_file)}'))

        if failed:
            util.exit_with_error('Failed to generate some output files.')
        else:
            print(util.info('Successfully generated all output files.'))

    def calculate_md5_sums(self):
        """
        Calculates md5 sums for each test.
        :return: Tuple (dictionary of md5 sums, list of outputs tests that need to be generated)
        """
        old_md5_sums = None
        if os.path.exists(os.path.join(os.getcwd(), 'in', '.md5sums')):
            lines = open(os.path.join(os.getcwd(), 'in', '.md5sums')).readlines()
            # If there is only one line, then the file is old format (without yaml, md5 sum of all files)
            if len(lines) > 1:
                try:
                    old_md5_sums = yaml.load("\n".join(lines), Loader=yaml.FullLoader)
                except yaml.YAMLError:
                    pass

        solution_compiled = False
        md5_sums = {}
        outputs_to_generate = []
        for file in glob.glob(os.path.join(os.getcwd(), 'in', '*.in')):
            basename = os.path.basename(file)
            md5_sums[basename] = hashlib.md5(open(file, 'rb').read()).hexdigest()
            if old_md5_sums is None or old_md5_sums.get(basename, '') != md5_sums[basename]:
                if not solution_compiled:
                    self.compile_correct_solution()
                    solution_compiled = True

                output_basename = os.path.splitext(os.path.basename(basename))[0] + '.out'
                outputs_to_generate.append(os.path.join(os.getcwd(), "out", output_basename))

        return md5_sums, outputs_to_generate

    def run(self, args: argparse.Namespace):
        if not util.check_if_project():
            util.exit_with_error('You are not in a project directory (couldn\'t find config.yml in current directory).')

        self.args = args
        self.task_id = package_util.get_task_id()
        self.ingen = gen_util.get_ingen(self.task_id, args.ingen_path)
        if self.ingen is None:
            util.exit_with_error(f'Couldn\'t find ingen source file.')
        print(util.info(f'Using ingen file {os.path.basename(self.ingen)}'))

        self.correct_solution = gen_util.get_correct_solution(self.task_id)
        if self.correct_solution is None:
            util.exit_with_error(f'Couldn\'t find correct solution file.')

        self.compile_ingen()
        if gen_util.run_ingen(self.ingen_exe):
            print(util.info('Successfully generated input files.'))
        else:
            util.exit_with_error('Failed to generate input files.')
        md5_sums, outputs_to_generate = self.calculate_md5_sums()
        self.generate_outputs(outputs_to_generate)
        with open(os.path.join(os.getcwd(), 'in', '.md5sums'), 'w') as f:
            yaml.dump(md5_sums, f)
