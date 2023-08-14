import os
import glob
import shutil
import tarfile
import tempfile
import argparse
import yaml

from sinol_make import util
from sinol_make.helpers import package_util, parsers
from sinol_make.commands.gen import gen_util
from sinol_make.interfaces.BaseCommand import BaseCommand


class Command(BaseCommand):
    """
    Class for "export" command.
    """

    def get_name(self):
        return "export"

    def configure_subparser(self, subparser: argparse.ArgumentParser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Create archive for oioioi upload',
            description='Creates archive ready to upload to oioioi.')

        parser.add_argument('-o', '--output', type=str, default='export',
                            help='output directory. Default: export')
        parsers.add_compilation_arguments(parser)

    def get_generated_tests(self):
        """
        Returns list of generated tests.
        Executes ingen to check what tests are generated.
        """
        if not gen_util.ingen_exists(self.task_id):
            return []

        with tempfile.TemporaryDirectory() as tmpdir:
            ingen_path = gen_util.get_ingen(self.task_id)
            if os.path.splitext(ingen_path)[1] == '.sh':
                ingen_exe = ingen_path
            else:
                ingen_exe = gen_util.compile_ingen(ingen_path, self.args, self.args.weak_compilation_flags)
            if not gen_util.run_ingen(ingen_exe, tmpdir):
                util.exit_with_error('Failed to run ingen.')

            tests = glob.glob(os.path.join(tmpdir, f'{self.task_id}*.in'))
            return [package_util.extract_test_id(test) for test in tests]

    def copy_files(self, target_dir: str):
        """
        Copies files from current directory to target directory.
        :param target_dir: Directory to copy files to.
        """
        files = ['config.yml', 'makefile.in', 'Makefile.in',
                 'prog', 'doc', 'public', 'dlazaw']
        for file in files:
            file_path = os.path.join(os.getcwd(), file)
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.copytree(file_path, os.path.join(target_dir, file))
                else:
                    shutil.copy(file_path, target_dir)

        print('Generating tests...')
        generated_tests = self.get_generated_tests()
        print('Copying only handwritten tests...')
        for ext in ['in', 'out']:
            os.mkdir(os.path.join(target_dir, ext))
            for test in glob.glob(os.path.join(os.getcwd(), ext, f'{self.task_id}*.{ext}')):
                if package_util.extract_test_id(test) not in generated_tests:
                    shutil.copy(test, os.path.join(target_dir, ext))

    def create_files(self, target_dir: str, config: dict):
        """
        Creates required files in target directory (makefile.in).
        :param target_dir: Directory to create files in.
        :param config: Config dictionary.
        """
        with open(os.path.join(target_dir, 'makefile.in'), 'w') as f:
            cxx_flags = '-std=c++17'
            c_flags = '-std=c17'
            if 'extra_compilation_args' in config:
                if 'cpp' in config['extra_compilation_args']:
                    cxx_flags += ' ' + ' '.join(config['extra_compilation_args']['cpp'])
                if 'c' in config['extra_compilation_args']:
                    c_flags += ' ' + ' '.join(config['extra_compilation_args']['c'])

            f.write(f'MODE = wer\n'
                    f'ID = {self.task_id}\n'
                    f'SIG = sinolmake\n'
                    f'\n'
                    f'TIMELIMIT = {config["time_limit"]}\n'
                    f'SLOW_TIMELIMIT = {4 * config["time_limit"]}\n'
                    f'MEMLIMIT = {config["memory_limit"]}\n'
                    f'\n'
                    f'OI_TIME = oiejq\n'
                    f'\n'
                    f'CXXFLAGS += {cxx_flags}\n'
                    f'CFLAGS += {c_flags}\n')

    def compress(self, tmpdir, target_dir):
        """
        Compresses target directory to archive.
        :param tmpdir: Temporary directory path.
        :param target_dir: Target directory path.
        :return: Path to archive.
        """
        archive = os.path.join(tmpdir, f'{self.task_id}.tgz')
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(target_dir, arcname=os.path.basename(target_dir))
        return archive

    def run(self, args: argparse.Namespace):
        if not util.check_if_project():
            print(util.warning('You are not in a project directory (couldn\'t find config.yml in current directory).'))
            exit(1)

        self.args = args
        export_dir = args.output or 'export'
        self.task_id = package_util.get_task_id()
        self.export_dir = os.path.abspath(export_dir)
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(os.getcwd(), 'config.yml'), 'r') as config_file:
                config = yaml.load(config_file, Loader=yaml.FullLoader)

            package_path = os.path.join(tmpdir, self.task_id)
            os.makedirs(package_path)

            self.copy_files(package_path)
            self.create_files(package_path, config)
            archive = self.compress(tmpdir, package_path)
            shutil.copy(archive, self.export_dir)

            print(util.info(f'Exported to {os.path.join(self.export_dir, self.task_id + ".tgz")}'))
