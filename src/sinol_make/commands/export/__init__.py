import os
import shutil
import tarfile
import tempfile
import argparse
import yaml

from sinol_make import util
from sinol_make.helpers import package_util
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
            description='Creates archive ready to upload to oioioi.'
        )

        parser.add_argument('-o', '--output', type=str, default='export',
                            help='output directory. Default: export')

    def copy_files(self, target_dir: str):
        files = ['config.yml', 'makefile.in', 'Makefile.in',
                 'in', 'out', 'prog', 'doc', 'public']
        for file in files:
            file_path = os.path.join(os.getcwd(), file)
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.copytree(file_path, os.path.join(target_dir, file))
                else:
                    shutil.copy(file_path, target_dir)

    def create_files(self, target_dir: str, task_id: str, config: dict):
        with open(os.path.join(target_dir, 'makefile.in'), 'w') as f:
            cxx_flags = '-std=c++17'
            c_flags = '-std=c17'
            if 'extra_compilation_args' in config:
                cxx_flags += ' ' + ' '.join(config['extra_compilation_args'].get('cpp', []))
                c_flags += ' ' + ' '.join(config['extra_compilation_args'].get('c', []))

            f.write(f'MODE = wer\n'
                    f'ID = {task_id}\n'
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

    def compress(self, tmpdir, target_dir, task_id):
        archive = os.path.join(tmpdir, f'{task_id}.tgz')
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(target_dir, arcname=os.path.basename(target_dir))
        return archive

    def run(self, args: argparse.Namespace):
        if not util.check_if_project():
            print(util.warning('You are not in a project directory (couldn\'t find config.yml in current directory).'))
            exit(1)

        export_dir = args.output or 'export'
        self.export_dir = os.path.abspath(export_dir)
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

        with open(os.path.join(os.getcwd(), 'config.yml'), 'r') as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)

        with tempfile.TemporaryDirectory() as tmpdir:
            task_id = package_util.get_task_id()
            package_path = os.path.join(tmpdir, task_id)
            os.makedirs(package_path)

            self.copy_files(package_path)
            self.create_files(package_path, task_id, config)
            archive = self.compress(tmpdir, package_path, task_id)
            shutil.copy(archive, self.export_dir)

        print(util.info(f'Exported to {os.path.join(self.export_dir, task_id + ".tgz")}'))
