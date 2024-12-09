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

    TEMPLATE_ID='__ID__'
    DEFAULT_TEMPLATE = 'https://github.com/sio2project/sinol-make.git'
    DEFAULT_SUBDIR = 'example_package'

    def get_name(self):
        return "init"

    def configure_subparser(self, subparser: argparse.ArgumentParser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Create package from the template',
            description='Create package from predefined template with given id.'
        )
        parser.add_argument('task_id', type=str, help='id of the task to create')
        parser.add_argument('-o', '--output', type=str,
            help='destination directory to copy the template into, defaults to task_id')
        parser.add_argument('-f', '--force', action='store_true',
            help='overwrite files in destination directory if they already exist')
        parser.add_argument('-t', '--template', nargs='+', default=[self.DEFAULT_TEMPLATE, self.DEFAULT_SUBDIR],
            help='specify template repository or directory, optionally subdirectory after space'
                f' (default: {self.DEFAULT_TEMPLATE} {self.DEFAULT_SUBDIR})')
        parser.add_argument('-v', '--verbose', action='store_true')
        return parser

    def download_template(self, tmpdir, template_paths = [DEFAULT_TEMPLATE, DEFAULT_SUBDIR], verbose = False):
        template = template_paths[0]
        subdir = template_paths[1] if len(template_paths) > 1 else ''

        is_url = template.startswith(('http://', 'https://', 'ssh://', 'git@', 'file://'))
        print(('Cloning' if is_url else 'Copying') + ' template ' +
            (f'{subdir} from {template}' if subdir else f'{template}'))
        if is_url:
            ret = subprocess.run(['git', 'clone', '-v' if verbose else '-q', '--depth', '1', template, tmpdir])
            if ret.returncode != 0:
                util.exit_with_error("Could not access repository. Please try again.")
            path = os.path.join(tmpdir, subdir)
        else:
            path = os.path.join(tmpdir, 'template')
            shutil.copytree(os.path.join(template, subdir), path)

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
                if file[:len(self.TEMPLATE_ID)] == self.TEMPLATE_ID:
                    dest_filename = self.task_id + file[len(self.TEMPLATE_ID):]
                shutil.move(os.path.join(root, file), os.path.join(mapping[root], dest_filename))

    def update_task_id(self):
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                path = os.path.join(os.getcwd(), root, file)
                with open(path) as file:
                    try:
                        file_data = file.read()
                    except UnicodeDecodeError:
                        # ignore non-text files
                        continue
                file_data = file_data.replace(self.TEMPLATE_ID, self.task_id)

                with open(path, 'w') as file:
                    file.write(file_data)

    def run(self, args: argparse.Namespace):
        self.task_id = args.task_id
        self.force = args.force
        destination = args.output or self.task_id
        if not os.path.isabs(destination):
            destination = os.path.join(os.getcwd(), destination)
        try:
            os.mkdir(destination)
        except FileExistsError:
            if not args.force:
                util.exit_with_error(f"Destination {destination} already exists. "
                                     f"Provide a different task id or directory name, "
                                     f"or use the --force flag to overwrite.")
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                self.template_dir = self.download_template(tmpdir, args.template, args.verbose)

                os.chdir(destination)

                self.move_folder()
                self.update_task_id()

                print(util.info(f'Successfully created task "{self.task_id}"'))
            except:
                shutil.rmtree(destination)
                raise
