import os
import glob
import stat
import shutil
import tarfile
import tempfile
import argparse

from sinol_make import util, contest_types
from sinol_make.commands.ingen.ingen_util import get_ingen, compile_ingen, run_ingen, ingen_exists
from sinol_make.helpers import package_util, parsers, paths
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.commands.outgen import Command as OutgenCommand, compile_correct_solution, get_correct_solution
from sinol_make.commands.doc import Command as DocCommand
from sinol_make.interfaces.Errors import UnknownContestType


class Command(BaseCommand):
    """
    Class for "export" command.
    """

    def get_name(self):
        return "export"

    def get_short_name(self):
        return "e"

    def configure_subparser(self, subparser: argparse.ArgumentParser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Create archive for oioioi upload',
            description='Creates archive in the current directory ready to upload to sio2 or szkopul.')
        parsers.add_cpus_argument(parser, 'number of cpus to use to generate output files')
        parser.add_argument('--no-statement', dest='no_statement', action='store_true',
                            help='allow export without statement')
        parser.add_argument('--export-ocen', dest='export_ocen', action='store_true',
                            help='Create ocen archive')
        parsers.add_compilation_arguments(parser)
        return parser

    def generate_input_tests(self):
        print('Generating tests...')
        temp_package = paths.get_cache_path('export', 'tests')
        if os.path.exists(temp_package):
            shutil.rmtree(temp_package)
        os.makedirs(temp_package)
        in_dir = os.path.join(temp_package, 'in')
        os.makedirs(in_dir)
        out_dir = os.path.join(temp_package, 'out')
        os.makedirs(out_dir)
        prog_dir = os.path.join(temp_package, 'prog')
        if os.path.exists(os.path.join(os.getcwd(), 'prog')):
            shutil.copytree(os.path.join(os.getcwd(), 'prog'), prog_dir)

        if ingen_exists(self.task_id):
            ingen_path = get_ingen(self.task_id)
            ingen_path = os.path.join(prog_dir, os.path.basename(ingen_path))
            ingen_exe = compile_ingen(ingen_path, self.args, self.args.compile_mode)
            if not run_ingen(ingen_exe, in_dir):
                util.exit_with_error('Failed to run ingen.')

    def generate_output_files(self):
        tests = paths.get_cache_path('export', 'tests')
        in_dir = os.path.join(tests, 'in')
        os.makedirs(in_dir, exist_ok=True)
        out_dir = os.path.join(tests, 'out')
        os.makedirs(out_dir, exist_ok=True)

        # Only example output tests are required for export.
        ocen_tests = glob.glob(os.path.join(in_dir, f'{self.task_id}0*.in')) + \
                     glob.glob(os.path.join(in_dir, f'{self.task_id}*ocen.in'))
        outputs = []
        for test in ocen_tests:
            outputs.append(os.path.join(out_dir, os.path.basename(test).replace('.in', '.out')))
        if len(outputs) > 0:
            outgen = OutgenCommand()
            correct_solution_exe = compile_correct_solution(get_correct_solution(self.task_id), self.args,
                                                            self.args.compile_mode)
            outgen.args = self.args
            outgen.correct_solution_exe = correct_solution_exe
            outgen.generate_outputs(outputs)

    def get_generated_tests(self):
        """
        Returns list of generated tests.
        Executes ingen to check what tests are generated.
        """
        if not ingen_exists(self.task_id):
            return []

        in_dir = paths.get_cache_path('export', 'tests', 'in')
        tests = glob.glob(os.path.join(in_dir, f'{self.task_id}*.in'))
        return [package_util.extract_test_id(test, self.task_id) for test in tests]

    def create_ocen(self, target_dir: str):
        """
        Creates ocen archive for sio2.
        :param target_dir: Path to exported package.
        """
        print('Generating ocen archive...')
        attachments_dir = os.path.join(target_dir, 'attachments')
        if not os.path.exists(attachments_dir):
            os.makedirs(attachments_dir)
        tests_dir = paths.get_cache_path('export', 'tests')

        with tempfile.TemporaryDirectory() as tmpdir:
            ocen_dir = os.path.join(tmpdir, self.task_id)
            os.makedirs(ocen_dir)
            in_dir = os.path.join(ocen_dir, 'in')
            os.makedirs(in_dir)
            out_dir = os.path.join(ocen_dir, 'out')
            os.makedirs(out_dir)
            num_tests = 0
            for ext in ['in', 'out']:
                for test in glob.glob(os.path.join(tests_dir, ext, f'{self.task_id}0*.{ext}')) + \
                            glob.glob(os.path.join(tests_dir, ext, f'{self.task_id}*ocen.{ext}')):
                    shutil.copy(test, os.path.join(ocen_dir, ext, os.path.basename(test)))
                    num_tests += 1

            dlazaw_dir = os.path.join(os.getcwd(), 'dlazaw')
            if num_tests == 0:
                print(util.warning('No ocen tests found.'))
            elif os.path.exists(dlazaw_dir):
                print(util.warning('Skipping ocen archive creation because dlazaw directory exists.'))
            else:
                shutil.make_archive(os.path.join(attachments_dir, f'{self.task_id}ocen'), 'zip', tmpdir)

            if os.path.exists(dlazaw_dir):
                print('Archiving dlazaw directory and adding to attachments.')
                os.makedirs(os.path.join(tmpdir, 'dlazaw'), exist_ok=True)
                shutil.copytree(dlazaw_dir, os.path.join(tmpdir, 'dlazaw', 'dlazaw'))
                shutil.make_archive(os.path.join(attachments_dir, 'dlazaw'), 'zip',
                                    os.path.join(tmpdir, 'dlazaw'))

    def compile_statement(self):
        command = DocCommand()
        doc_args = argparse.Namespace()
        doc_args.files = [f'./doc/{self.task_id}zad.tex']
        command.run(doc_args)
        if not os.path.isfile(f'./doc/{self.task_id}zad.pdf') and not self.args.no_statement:
            util.exit_with_error('There is no pdf statements. If this intentional, export with flag "--no-statement". '
                                 'Otherwise create pdf before continuing.')

    def copy_package_required_files(self, target_dir: str):
        """
        Copies package files and directories from
        current directory to target directory.
        :param target_dir: Directory to copy files to.
        """
        files = ['config.yml', 'makefile.in', 'Makefile.in',
                 'prog', 'doc', 'attachments', 'dlazaw']
        for file in files:
            file_path = os.path.join(os.getcwd(), file)
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.copytree(file_path, os.path.join(target_dir, file))
                else:
                    shutil.copy(file_path, target_dir)
        shell_ingen = os.path.join(target_dir, 'prog', f'{self.task_id}ingen.sh')
        if os.path.exists(shell_ingen):
            st = os.stat(shell_ingen)
            os.chmod(shell_ingen, st.st_mode | stat.S_IEXEC)

        print('Copying example tests...')
        for ext in ['in', 'out']:
            os.mkdir(os.path.join(target_dir, ext))
            for test in glob.glob(os.path.join(os.getcwd(), ext, f'{self.task_id}0*.{ext}')):
                shutil.copy(test, os.path.join(target_dir, ext))

        generated_tests = self.get_generated_tests()
        tests_to_copy = []
        for ext in ['in', 'out']:
            for test in glob.glob(os.path.join(os.getcwd(), ext, f'{self.task_id}*.{ext}')):
                if package_util.extract_test_id(test, self.task_id) not in generated_tests:
                    tests_to_copy.append((ext, test))

        cache_test_dir = paths.get_cache_path('export', 'tests')
        if len(tests_to_copy) > 0:
            print(util.warning(f'Found {len(tests_to_copy)} tests that are not generated by ingen.'))
            for test in tests_to_copy:
                print(util.warning(f'Copying {os.path.basename(test[1])}...'))
                shutil.copy(test[1], os.path.join(target_dir, test[0], os.path.basename(test[1])))
                shutil.copy(test[1], os.path.join(cache_test_dir, test[0], os.path.basename(test[1])))

        self.generate_output_files()
        if self.args.export_ocen:
            self.create_ocen(target_dir)

    def clear_files(self, target_dir: str):
        """
        Clears unnecessary files from target directory.
        :param target_dir: Directory to clear files from.
        """
        files_to_remove = ['doc/*~', 'doc/*.aux', 'doc/*.log', 'doc/*.dvi', 'doc/*.err', 'doc/*.inf']
        for pattern in files_to_remove:
            for f in glob.glob(os.path.join(target_dir, pattern)):
                os.remove(f)

    def create_makefile_in(self, target_dir: str, config: dict):
        """
        Creates required `makefile.in` file.
        :param target_dir: Directory to create files in.
        :param config: Config dictionary.
        """
        with open(os.path.join(target_dir, 'makefile.in'), 'w') as f:
            cxx_flags = '-std=c++20'
            c_flags = '-std=gnu99'

            def format_multiple_arguments(obj):
                if isinstance(obj, str):
                    return obj
                return ' '.join(obj)

            # Only use extra_compilation_args for compiling solution files.
            # One usecase of this is "reverse-library" problem packages,
            # that provide a main.cpp file to be compiled with submissions.
            # If extra args need to be passed to chk/ingen/inwer in the future,
            # support for a new separate config option will have to be added.
            extra_cxx_args = ""
            extra_c_args = ""
            if 'extra_compilation_args' in config:
                if 'cpp' in config['extra_compilation_args']:
                    extra_cxx_args = format_multiple_arguments(config['extra_compilation_args']['cpp'])
                if 'c' in config['extra_compilation_args']:
                    extra_c_args = format_multiple_arguments(config['extra_compilation_args']['c'])

            tl = config.get('time_limit', None)
            if not tl:
                tl = config['time_limits'][0]
            f.write(f'MODE = wer\n'
                    f'ID = {self.task_id}\n'
                    f'SIG = sinolmake\n'
                    f'\n'
                    f'TIMELIMIT = {tl}\n'
                    f'SLOW_TIMELIMIT = {4 * tl}\n'
                    f'MEMLIMIT = {config["memory_limit"]}\n'
                    f'\n'
                    f'OI_TIME = oiejq\n'
                    f'\n'
                    f'CXXFLAGS += {cxx_flags}\n'
                    f'{self.task_id}chk.e: CXXFLAGS := $(CXXFLAGS)\n'
                    f'{self.task_id}ingen.e: CXXFLAGS := $(CXXFLAGS)\n'
                    f'{self.task_id}inwer.e: CXXFLAGS := $(CXXFLAGS)\n'
                    f'CXXFLAGS += {extra_cxx_args}\n'
                    f'\n'
                    f'CFLAGS += {c_flags}\n'
                    f'{self.task_id}chk.e: CFLAGS := $(CFLAGS)\n'
                    f'{self.task_id}ingen.e: CFLAGS := $(CFLAGS)\n'
                    f'{self.task_id}inwer.e: CFLAGS := $(CFLAGS)\n'
                    f'CFLAGS += {extra_c_args}\n')

    def compress(self, target_dir):
        """
        Compresses target directory to archive.
        :param target_dir: Target directory path.
        :return: Path to archive.
        """
        archive = os.path.join(os.getcwd(), f'{self.export_name}.tgz')
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(target_dir, arcname=os.path.basename(target_dir))
        return archive

    def run(self, args: argparse.Namespace):
        args = util.init_package_command(args)

        self.args = args
        self.task_id = package_util.get_task_id()
        self.export_name = self.task_id
        package_util.validate_test_names(self.task_id)
        try:
            self.contest = contest_types.get_contest_type()
        except UnknownContestType as e:
            util.exit_with_error(str(e))

        config = package_util.get_config()

        export_package_path = paths.get_cache_path('export', self.task_id)
        if os.path.exists(export_package_path):
            shutil.rmtree(export_package_path)
        os.makedirs(export_package_path)

        util.change_stack_size_to_unlimited()
        self.generate_input_tests()
        self.compile_statement()
        self.copy_package_required_files(export_package_path)
        self.clear_files(export_package_path)
        self.create_makefile_in(export_package_path, config)
        export_name = self.contest.additional_export_job()
        if export_name is not None:
            self.export_name = export_name
        archive = self.compress(export_package_path)

        print(util.info(f'Exported to {self.export_name}.tgz'))
