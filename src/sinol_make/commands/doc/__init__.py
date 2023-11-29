import os
import glob
import argparse
import subprocess

from sinol_make import util
from sinol_make.helpers import paths
from sinol_make.interfaces.BaseCommand import BaseCommand


class Command(BaseCommand):
    """
    Class for `doc` command.
    """
    LOG_PATTERNS = ['*~', '*.aux', '*.log', '*.dvi', '*.err', '*.inf']

    def get_name(self):
        return "doc"

    def compile_file(self, file_path):
        print(util.info(f'Compiling {os.path.basename(file_path)}...'))
        os.chdir(os.path.dirname(file_path))
        subprocess.run(['latex', file_path])
        dvi_file = os.path.splitext(file_path)[0] + '.dvi'
        dvi_file_path = os.path.join(os.path.dirname(file_path), dvi_file)
        if not os.path.exists(dvi_file_path):
            print(util.error('Compilation failed.'))
            return False

        process = subprocess.run(['dvipdf', dvi_file_path])
        if process.returncode != 0:
            print(util.error('Compilation failed.'))
            return False
        print(util.info(f'Compilation successful for file {os.path.basename(file_path)}.'))
        return True

    def move_logs(self):
        output_dir = paths.get_cache_path('doc_logs')
        os.makedirs(output_dir, exist_ok=True)
        for pattern in self.LOG_PATTERNS:
            for file in glob.glob(os.path.join(os.getcwd(), 'doc', pattern)):
                os.rename(file, os.path.join(output_dir, os.path.basename(file)))
        print(util.info(f'Compilation log files can be found in {os.path.relpath(output_dir, os.getcwd())}'))

    def configure_subparser(self, subparser: argparse.ArgumentParser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Compile latex files to pdf',
            description='Compiles latex files to pdf. By default compiles all files in the `doc` directory.\n'
                        'You can also specify files to compile.')
        parser.add_argument('files', type=str, nargs='*', help='files to compile')

    def run(self, args: argparse.Namespace):
        util.exit_if_not_package()

        if args.files == []:
            self.files = glob.glob(os.path.join(os.getcwd(), 'doc', '*.tex'))
        else:
            self.files = []
            for file in args.files:
                if not os.path.exists(file):
                    print(util.warning(f'File {file} does not exist.'))
                else:
                    self.files.append(os.path.abspath(file))
        if self.files == []:
            print(util.warning('No files to compile.'))
            return

        original_cwd = os.getcwd()
        failed = []
        for file in self.files:
            if not self.compile_file(file):
                failed.append(file)
        os.chdir(original_cwd)

        self.move_logs()
        if failed:
            for failed_file in failed:
                print(util.error(f'Failed to compile {failed_file}'))
            util.exit_with_error('Compilation failed.')
        else:
            print(util.info('Compilation was successful for all files.'))
