import argparse
import os
import shutil
import subprocess
import tempfile

from sinol_make import util
from sinol_make.interfaces.BaseCommand import BaseCommand


class Command(BaseCommand):
    """
    Class for "init"
    """

    def get_name(self):
        return "init"

    def configure_subparser(self, subparser: argparse.ArgumentParser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Create package from the template',
            description='Create package from predefined template with given id.'
        )
        parser.add_argument('task_id', type=str, help='id of the task to create')
        parser.add_argument('directory', type=str, nargs='?',
            help='destination directory to copy the template into, defaults to task_id')
        parser.add_argument('-f', '--force', action='store_true',
            help='overwrite files in destination directory if they already exist')
        return parser

    def download_template(self):
        repo = 'https://github.com/sio2project/sinol-make.git'
        package_dir = 'sinol-make/example_package'
        self.used_tmpdir = tempfile.TemporaryDirectory()
        tmp_dir = self.used_tmpdir.name
        ret = subprocess.run(['git', 'clone', '-q', '--depth', '1', repo], cwd=tmp_dir)
        if ret.returncode != 0:
            util.exit_with_error("Could not access repository. Please try again.")
        path = os.path.join(tmp_dir, package_dir)
        if os.path.exists(os.path.join(path, '.git')):
            shutil.rmtree(os.path.join(path, '.git'))
        return path

    def move_folder(self):
        mapping = {}
        mapping[self.template_dir] = os.getcwd()
        for root, dirs, files in os.walk(self.template_dir):
            for directory in dirs:
                mapping[os.path.join(root, directory)] = os.path.join(mapping[root], directory)
                try:
                    os.mkdir(os.path.join(mapping[root], directory))
                except FileExistsError:
                    if not self.force:
                        raise
            for file in files:
                dest_filename = file
                if file[:3] == 'abc':
                    dest_filename = self.task_id + file[3:]
                shutil.move(os.path.join(root, file), os.path.join(mapping[root], dest_filename))

    def update_config(self):
        with open(os.path.join(os.getcwd(), 'config.yml')) as config:
            config_data = config.read()
        config_data = config_data.replace('sinol_task_id: abc', f'sinol_task_id: {self.task_id}')

        with open(os.path.join(os.getcwd(), 'config.yml'), 'w') as config:
            config.write(config_data)

    def run(self, args: argparse.Namespace):
        self.task_id = args.task_id
        self.force = args.force
        destination = args.directory or self.task_id
        if not os.path.isabs(destination):
            destination = os.path.join(os.getcwd(), destination)
        try:
            os.mkdir(destination)
        except FileExistsError:
            if not args.force:
                util.exit_with_error(f"Destination {destination} already exists. "
                                     f"Provide a different task id or directory name, "
                                     f"or use the --force flag to overwrite.")
        os.chdir(destination)

        self.template_dir = self.download_template()

        self.move_folder()
        self.update_config()

        self.used_tmpdir.cleanup()

        print(util.info(f'Successfully created task "{self.task_id}"'))
