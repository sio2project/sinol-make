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
        parser.add_argument('task_id', type=str, help='Id of the task to create')

    def download_template(self):
        repo = 'https://github.com/sio2project/sinol-make.git'
        package_dir = 'sinol-make/example_package'
        self.used_tmpdir = tempfile.TemporaryDirectory()
        tmp_dir = self.used_tmpdir.name
        ret = subprocess.run(['git', 'clone', '-q', '--depth', '1', repo], cwd=tmp_dir)
        if ret.returncode != 0:
            util.exit_with_error("Could not access repository. Please try again.")
        return os.path.join(tmp_dir, package_dir)

    def move_folder(self):
        mapping = {}
        mapping[self.template_dir] = os.getcwd()
        for root, dirs, files in os.walk(self.template_dir):
            for directory in dirs:
                mapping[os.path.join(root, directory)] = os.path.join(mapping[root], directory)
                os.mkdir(os.path.join(mapping[root], directory))
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
        destination = os.path.join(os.getcwd(), args.task_id)
        if os.path.isdir(destination) or os.path.isfile(destination):
            util.exit_with_error(f"Cannot create task {args.task_id}, this name is already used in current directory. "
                                 f"Remove the file/folder with this name or choose another id.")

        self.template_dir = self.download_template()

        os.mkdir(os.path.join(os.getcwd(), self.task_id))
        os.chdir(os.path.join(os.getcwd(), self.task_id))

        self.move_folder()
        self.update_config()
        
        self.used_tmpdir.cleanup()

        print(util.info(f'Successfully created task "{self.task_id}"'))

