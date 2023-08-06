import os
import glob
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
            description='Creates archive ready to upload to oioioi. '
                        'It is possible to create ocen and dlazaw debian packages for usage in contests '
                        'with --ocen flag.'
        )

        parser.add_argument('-o', '--output', type=str, default='export',
                            help='output directory. Default: export')
        parser.add_argument('--ocen', action='store_true', default=False,
                            help='create ocen (or dlazaw in case `dlazaw/` directory exists) debian package '
                                 'for usage in contests')

    def copy_files(self, target_dir: str):
        """
        Copies files from current directory to target directory.
        :param target_dir: Directory to copy files to.
        """
        files = ['config.yml', 'makefile.in', 'Makefile.in',
                 'in', 'out', 'prog', 'doc', 'public', 'dlazaw']
        for file in files:
            file_path = os.path.join(os.getcwd(), file)
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.copytree(file_path, os.path.join(target_dir, file))
                else:
                    shutil.copy(file_path, target_dir)

    def create_files(self, target_dir: str, task_id: str, config: dict):
        """
        Creates required files in target directory (makefile.in).
        :param target_dir: Directory to create files in.
        :param task_id: Task id.
        :param config: Config dictionary.
        """
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
        """
        Compresses target directory to archive.
        :param tmpdir: Temporary directory path.
        :param target_dir: Target directory path.
        :param task_id: Task id.
        :return: Path to archive.
        """
        archive = os.path.join(tmpdir, f'{task_id}.tgz')
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(target_dir, arcname=os.path.basename(target_dir))
        return archive

    def copy_test(self, ocen_dir, filename):
        """
        Copies test to ocen directory.
        :param ocen_dir: Ocen directory path.
        :param filename: Test filename.
        """
        base = os.path.basename(filename)
        ext = base.split('.')[-1]
        out = os.path.join(ocen_dir, ext, base)
        shutil.copyfile(filename, out)

    def ocen_gen_conf(self, ocen_dir, nums, task_id):
        """
        Generates ocen configuration file.
        :param ocen_dir: Ocen directory path.
        :param nums: Set of test numbers.
        :param task_id: Task id.
        """

        print("Generating ocen configuration file...")
        with open(os.path.join(ocen_dir, 'oi.conf'), "w") as conf:
            conf.write(f'TASKS="{task_id}"\n'
                       f'TESTS_{task_id}="{" ".join(sorted(nums))}"\n'
                       f'HARD_TIMELIMIT=60    # limit czasu na wykonanie pod oitimetool (zwroc  uwage,\n'
                       f'                     # ze nie ma to nic wspolnego z wynikiem oitimetool dla Twojego programu)\n'
                       f'MEMLIMIT=1000000   # limit wykorzysztania pamieci przez program oraz oitimetool (KiB)\n'
                       f'SRCLIMIT=100     # limit na rozmiar pliku zrodlowego (KiB)\n'
                       f'EXELIMIT=10240   # limit na rozmiar pliku wykonywalnego (KiB) = 10MB\n')

    def build_debian_package(self, package_path, package_dir_name):
        """
        Builds debian package.
        :param package_path: Path to directory with package.
        :param package_dir_name: Name of directory with package.
        :return: Path to .deb file.
        """
        deb_path = os.path.join(package_path, package_dir_name)
        os.chmod(os.path.join(deb_path, 'DEBIAN'), 0o755)
        for root, dirs, files in os.walk(os.path.join(deb_path, 'DEBIAN')):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o755)
            for f in files:
                os.chmod(os.path.join(root, f), 0o755)
                util.fix_line_endings(os.path.join(root, f))

        exit_code = os.system(f'cd {package_path} && dpkg-deb -v -Zxz --build {package_dir_name}')
        if exit_code != 0:
            util.exit_with_error("Failed to create debian package.")

        return os.path.join(package_path, f'{package_dir_name}.deb')

    def ocen_make_deb_package(self, tmpdir, ocen_dir, task_id):
        """
        Creates ocen debian package.
        :param tmpdir: Temporary directory path.
        :param ocen_dir: Ocen directory path.
        :return: Path to debian package.
        """
        deb_template = os.path.abspath(os.path.join(util.get_templates_dir(), 'oi-ocen'))
        deb_dir = os.path.join(tmpdir, f'oi-ocen-{task_id}')
        shutil.copytree(deb_template, deb_dir)

        print("Creating archive with ocen...")
        with tarfile.open(os.path.join(tmpdir, 'ocen-linux.tgz'), 'w:gz') as tar:
            tar.add(ocen_dir, arcname=os.path.basename(ocen_dir))

        print("Creating debian package...")
        os.makedirs(os.path.join(deb_dir, 'usr', 'share', f'oi-ocen-{task_id}'), exist_ok=True)
        shutil.copyfile(os.path.join(tmpdir, 'ocen-linux.tgz'),
                        os.path.join(deb_dir, 'usr', 'share', f'oi-ocen-{task_id}', 'ocen-linux.tgz'))

        def replace_text(file, old, new):
            with open(file, 'r') as f:
                content = f.read().replace(old, new)
            with open(file, 'w') as f:
                f.write(content)

        replace_text(os.path.join(deb_dir, 'DEBIAN', 'control'), 'TASK_ID', task_id)
        replace_text(os.path.join(deb_dir, 'DEBIAN', 'postinst'), 'task_id = None', f'task_id = "{task_id}"')

        return self.build_debian_package(tmpdir, f'oi-ocen-{task_id}')

    def make_ocen(self, tmpdir, task_id):
        """
        Creates ocen debian package for contests.
        :param tmpdir: Temporary directory path.
        :return: Path to ocen package.
        """

        print("Copying ocen template...")
        ocen_template = os.path.abspath(os.path.join(util.get_templates_dir(), 'ocen-linux-sio2jail'))
        ocen_dir = os.path.join(tmpdir, 'rozw')
        shutil.copytree(ocen_template, ocen_dir)
        for d in ['in', 'out']:
            shutil.rmtree(os.path.join(ocen_dir, d))
            os.mkdir(os.path.join(ocen_dir, d), 0o755)

        for root, dirs, files in os.walk(ocen_dir):
            for f in files:
                util.fix_line_endings(os.path.join(root, f))

        test_patterns = [
            'in/???0*.in',
            'in/*ocen.in',
            'out/???0*.out',
            'out/*ocen.out',
        ]

        nums = set()
        for pattern in test_patterns:
            for file in glob.glob(os.path.join(os.getcwd(), pattern)):
                self.copy_test(ocen_dir, file)
                nums.add(os.path.basename(file).split('.')[0][3:])

        self.ocen_gen_conf(ocen_dir, nums, task_id)
        return self.ocen_make_deb_package(tmpdir, ocen_dir, task_id)

    def make_dlazaw(self, tmpdir, task_id):
        """
        Creates dlazaw debian package for contests.
        :param tmpdir: Temporary directory path.
        :param task_id: Task id.
        """

        print("Copying dlazaw template...")
        shutil.copytree(os.path.join(util.get_templates_dir(), 'oi-dlazaw'),
                        os.path.join(tmpdir, 'oi-dlazaw'))

        shutil.copytree(os.path.join(os.getcwd(), 'dlazaw'),
                        os.path.join(tmpdir, 'oi-dlazaw', 'home', 'zawodnik', 'dlazaw'))

        print("Creating debian package...")
        return self.build_debian_package(tmpdir, 'oi-dlazaw')

    def run(self, args: argparse.Namespace):
        if not util.check_if_project():
            print(util.warning('You are not in a project directory (couldn\'t find config.yml in current directory).'))
            exit(1)

        export_dir = args.output or 'export'
        task_id = package_util.get_task_id()
        self.export_dir = os.path.abspath(export_dir)
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)

        with tempfile.TemporaryDirectory() as tmpdir:
            if args.ocen:
                if os.path.exists(os.path.join(os.getcwd(), 'dlazaw')):
                    print("Creating dlazaw debian package...")
                    deb_file = self.make_dlazaw(tmpdir, task_id)
                else:
                    print("Creating ocen debian package...")
                    deb_file = self.make_ocen(tmpdir, task_id)

                shutil.copy(deb_file, self.export_dir)
                print(util.info(f'Exported to {os.path.join(self.export_dir, os.path.basename(deb_file))}'))
            else:
                with open(os.path.join(os.getcwd(), 'config.yml'), 'r') as config_file:
                    config = yaml.load(config_file, Loader=yaml.FullLoader)

                package_path = os.path.join(tmpdir, task_id)
                os.makedirs(package_path)

                self.copy_files(package_path)
                self.create_files(package_path, task_id, config)
                archive = self.compress(tmpdir, package_path, task_id)
                shutil.copy(archive, self.export_dir)

                print(util.info(f'Exported to {os.path.join(self.export_dir, task_id + ".tgz")}'))
