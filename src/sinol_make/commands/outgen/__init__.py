import argparse
import glob
import os
import yaml

from typing import Dict, List, Tuple, Union
import multiprocessing as mp

from sinol_make import util
from sinol_make.commands.outgen.outgen_util import get_correct_solution, compile_correct_solution, generate_output
from sinol_make.structs.gen_structs import OutputGenerationArguments, OutputVerificationArguments
from sinol_make.helpers import parsers, package_util, cache, compile, compiler, paths
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
        parsers.add_cpus_argument(parser, 'number of cpus to use to generate output files')
        parser.add_argument('-n', '--no-validate', default=False, action='store_true',
                            help='do not validate test contents')
        parsers.add_overwrite_argument(parser)
        parsers.add_compilation_arguments(parser)
        return parser

    def generate_outputs(self, outputs_to_generate, from_inputs=None) -> Dict[str, str]:
        """
        Generates the given output files with the correct solution.
        :param outputs_to_generate: List of paths of output files to generate.
        :param from_inputs: List of paths of input files to generate the outputs from. If None, the inputs
                            are assumed to be in the `in` directory next to the outputs' directory.
        :return: Dictionary mapping the basename of each generated output to its md5 sum.
        """
        arguments = []
        for i, output in enumerate(outputs_to_generate):
            output_basename = os.path.basename(output)
            if from_inputs is not None:
                input = from_inputs[i]
            else:
                in_dir = os.path.join("/", *(os.path.abspath(output).split(os.sep)[:-2]), 'in')
                input = os.path.join(in_dir, os.path.splitext(output_basename)[0] + '.in')
            arguments.append(OutputGenerationArguments(self.correct_solution_exe, input, output))

        print(f'Generating output files for {len(outputs_to_generate)} tests on {self.args.cpus} cpus.')
        md5_sums = self.run_generation(arguments)
        print(util.info('Successfully generated all output files.'))
        return md5_sums

    def run_generation(self, arguments: List[OutputGenerationArguments]) -> Dict[str, str]:
        """
        Generates output files for the given arguments in parallel.
        Exits with an error if any of the output files couldn't be generated.
        :return: Dictionary mapping the basename of each generated output to its md5 sum.
        """
        with mp.Pool(self.args.cpus) as pool:
            results = []
            md5_sums = {}
            for i, (result, stderr, md5_sum) in enumerate(pool.imap(generate_output, arguments)):
                results.append(result)
                output_file = os.path.basename(arguments[i].output_test)
                if stderr:
                    print(util.error(f'Outgen stderr on {output_file}:'))
                    print(stderr.decode('utf-8'), end='\n\n')
                if result:
                    md5_sums[output_file] = md5_sum
                    print(f'Successfully generated output file {output_file}')
                else:
                    print(util.error(f'Failed to generate output file {output_file}'))

            if not all(results):
                util.exit_with_error('Failed to generate some output files.')
            return md5_sums

    def calculate_md5_sums(self, tests=None):
        """
        Calculates md5 sums for each test.
        :return: Tuple (dictionary of md5 sums, list of outputs tests that need to be generated,
                 list of input tests based on which the output tests will be generated)
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
        from_inputs = []
        for file in tests:
            basename = os.path.basename(file)
            output_basename = os.path.splitext(os.path.basename(basename))[0] + '.out'
            output_path = os.path.join(os.getcwd(), 'out', output_basename)
            md5_sums[basename] = util.get_file_md5(file)

            if old_md5_sums is None or old_md5_sums.get(basename, '') != md5_sums[basename]:
                outputs_to_generate.append(output_path)
                from_inputs.append(file)
            elif not os.path.exists(output_path):
                # If output file does not exist, generate it.
                outputs_to_generate.append(output_path)
                from_inputs.append(file)

        return md5_sums, outputs_to_generate, from_inputs

    @staticmethod
    def get_generated_outputs_path():
        """
        Returns path to the file which keeps track of output files generated by sinol-make.
        """
        return os.path.join(os.getcwd(), 'out', '.md5sums')

    def load_generated_outputs(self) -> Union[Dict[str, str], None]:
        """
        Returns a dictionary mapping the basename of every output file generated by sinol-make
        to its md5 sum from when it was generated. Output files which are missing from this dictionary
        or whose md5 sum doesn't match weren't generated by sinol-make (they were, for example,
        written by hand) and must not be overwritten.
        :return: The dictionary or None if the package doesn't keep track of generated outputs yet.
        """
        try:
            with open(self.get_generated_outputs_path(), 'r') as f:
                file_content = yaml.load(f, Loader=yaml.FullLoader)
                if isinstance(file_content, dict):
                    return file_content
        except FileNotFoundError:
            return None
        except (yaml.YAMLError, OSError):
            pass
        print(util.warning('File out/.md5sums is corrupted. '
                           'All output files will be treated as if they were written by hand.'))
        return {}

    def save_generated_outputs(self, generated_outputs: Dict[str, str]):
        """
        Saves the md5 sums of output files generated by sinol-make.
        """
        os.makedirs(os.path.join(os.getcwd(), 'out'), exist_ok=True)
        with open(self.get_generated_outputs_path(), 'w') as f:
            yaml.dump(generated_outputs, f)

    def create_generated_outputs(self) -> Dict[str, str]:
        """
        Creates the initial list of generated output files for packages which were created with
        versions of sinol-make that didn't keep track of them. Every output file except the example ones
        is assumed to have been generated by sinol-make, as example outputs are the ones which are
        usually written by hand (and the only ones kept in the repository).
        """
        generated_outputs = {}
        for output in glob.glob(os.path.join(os.getcwd(), 'out', f'{self.task_id}*.out')):
            try:
                is_example = package_util.get_group(output, self.task_id) == 0
            except (AttributeError, ValueError):
                # If the group can't be determined, the output is treated as if it was written by hand.
                is_example = True
            if not is_example:
                generated_outputs[os.path.basename(output)] = util.get_file_md5(output)
        self.save_generated_outputs(generated_outputs)
        return generated_outputs

    def split_outputs(self, outputs_to_generate, from_inputs, generated_outputs: Dict[str, str]) \
            -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        Splits the tests into ones for which the output file can be overwritten and ones for which
        the output file wasn't generated by sinol-make and thus has to be verified instead.
        :return: Tuple of two lists of (input file, output file) pairs.
        """
        to_generate = []
        to_verify = []
        for input, output in zip(from_inputs, outputs_to_generate):
            basename = os.path.basename(output)
            if not os.path.exists(output) or generated_outputs.get(basename, None) == util.get_file_md5(output):
                to_generate.append((input, output))
            else:
                to_verify.append((input, output))
        return to_generate, to_verify

    def compile_checker(self):
        """
        Compiles the checker, if the package has one.
        """
        for additional_file in self.task_type.additional_files_to_compile():
            file_path, exe_path, name = additional_file[0], additional_file[1], additional_file[2]
            print(f'Compiling {name}... ', end='')
            compilers = compiler.verify_compilers(self.args, [file_path])
            exe, compile_log_path = compile.compile_file(file_path, exe_path, compilers, self.args.compile_mode,
                                                         use_sanitizers=self.args.sanitize, use_extras=False)
            if exe is None:
                print(util.error('ERROR'))
                util.exit_with_error(f'Failed {name} compilation.',
                                     lambda: compile.print_compile_log(compile_log_path))
            print(util.info('OK'))

    def verify_output(self, arguments: OutputVerificationArguments) -> Tuple[str, bool, str]:
        """
        Checks whether the output file which wasn't generated by sinol-make is correct.
        :return: Tuple of the verified output file, whether it is correct and the checker's comment.
        """
        ok, points, comment, _ = self.task_type.check_output(arguments.input_test, arguments.output_test,
                                                             arguments.model_output_test)
        return arguments.output_test, ok and points == 100, comment

    def verify_outputs(self, to_verify: List[Tuple[str, str]]):
        """
        Verifies output files which weren't generated by sinol-make instead of overwriting them.
        The correct solution's outputs are generated in the cache directory and the existing output files
        are checked against them (with the checker, if the package has one).
        Exits with an error if any of the verified output files is wrong.
        """
        print(f'{len(to_verify)} output files were not generated by sinol-make and won\'t be overwritten.')
        print(f'Generating the correct solution\'s outputs for them on {self.args.cpus} cpus.')
        self.task_type = package_util.get_task_type('time', None)
        arguments = [OutputGenerationArguments(self.correct_solution_exe, input,
                                               paths.get_outgen_path(os.path.basename(output)))
                     for input, output in to_verify]
        self.run_generation(arguments)
        self.compile_checker()

        print(f'Verifying {len(to_verify)} output files which were not generated by sinol-make.')

        executions = [OutputVerificationArguments(input, output, generation.output_test)
                      for (input, output), generation in zip(to_verify, arguments)]
        wrong = []
        with mp.Pool(self.args.cpus) as pool:
            for output, ok, comment in pool.imap(self.verify_output, executions):
                if ok:
                    print(util.info(f'Output file {os.path.basename(output)} is correct, leaving it unchanged.'))
                else:
                    wrong.append((output, comment))
                    print(util.error(f'Output file {os.path.basename(output)} is wrong.'
                                     + (f' Checker comment: {comment}' if comment else '')))

        if wrong:
            util.exit_with_error(
                f'{len(wrong)} output files which were not generated by sinol-make are wrong.\n'
                f'The correct solution\'s outputs for these tests were saved in {paths.get_outgen_path()}.\n'
                f'If they should be replaced with the correct solution\'s outputs, '
                f'run this command with the --overwrite flag.')
        print(util.info('All output files which were not generated by sinol-make are correct.'))

    def clean_cache(self, inputs):
        """
        Cleans cache for the given input files.
        """
        md5_sums = [util.get_file_md5(file) for file in inputs]
        for solution in glob.glob(paths.get_cache_path("md5sums", "*")):
            sol_cache = cache.get_cache_file(solution)
            for input in md5_sums:
                if input in sol_cache.tests:
                    del sol_cache.tests[input]
            sol_cache.save(solution)

    def run(self, args: argparse.Namespace):
        args = util.init_package_command(args)

        self.args = args
        self.task_id = package_util.get_task_id()
        self.task_type_cls = package_util.get_task_type_cls()
        if not self.task_type_cls.run_outgen():
            util.exit_with_error('Output generation is not supported for this task type.')
        package_util.validate_test_names(self.task_id)
        util.change_stack_size_to_unlimited()
        cache.check_correct_solution(self.task_id)
        self.correct_solution = get_correct_solution(self.task_id)

        md5_sums, outputs_to_generate, from_inputs = self.calculate_md5_sums()
        generated_outputs = self.load_generated_outputs()
        if generated_outputs is None:
            generated_outputs = self.create_generated_outputs()

        if self.args.overwrite:
            to_generate = list(zip(from_inputs, outputs_to_generate))
            to_verify = []
        else:
            to_generate, to_verify = self.split_outputs(outputs_to_generate, from_inputs, generated_outputs)

        if len(outputs_to_generate) == 0:
            print(util.info('All output files are up to date.'))
        else:
            self.clean_cache(from_inputs)
            self.correct_solution_exe = compile_correct_solution(self.correct_solution, self.args,
                                                                 self.args.compile_mode,
                                                                 use_sanitizers=self.args.sanitize)
            if to_generate:
                generated_outputs.update(self.generate_outputs([output for _, output in to_generate],
                                                               [input for input, _ in to_generate]))
                self.save_generated_outputs(generated_outputs)
            if to_verify:
                self.verify_outputs(to_verify)
            with open(os.path.join(os.getcwd(), 'in', '.md5sums'), 'w') as f:
                yaml.dump(md5_sums, f)

        if not self.args.no_validate:
            package_util.validate_tests(sorted(outputs_to_generate), self.args.cpus, 'outputs')
