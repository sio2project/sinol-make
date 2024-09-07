import os
import stat
import shutil
import argparse
import subprocess

from sinol_make import util, contest_types
from sinol_make.helpers import parsers, package_util, paths, cache
from sinol_make.interfaces.BaseCommand import BaseCommand
from sinol_make.commands.gen import Command as GenCommand
from sinol_make.commands.doc import Command as DocCommand
from sinol_make.commands.inwer import Command as InwerCommand, inwer_util
from sinol_make.commands.run import Command as RunCommand


class Command(BaseCommand):
    """
    Class for `verify` command.
    """

    def get_name(self):
        return "verify"

    def get_short_name(self):
        return "v"

    def configure_subparser(self, subparser):
        parser = subparser.add_parser(
            self.get_name(),
            help='Verify the package',
            description='Verify the whole package. This command will first '
                        'run stress tests (if the file `prog/{task_id}stresstest.sh` exists), '
                        'verify the config, generate tests, generate problem '
                        'statements, run inwer and run all solutions. '
                        'Ingen and inwer are compiled with sanitizers (-fsanitize=address,undefined), '
                        'which may fail on some systems. To fix this, run `sudo sysctl vm.mmap_rnd_bits = 28` '
                        'or disable sanitizers with --no-fsanitize.'
        )

        parser.add_argument('-e', '--expected-contest-type', type=str,
                            help='expected contest type. Fails if the actual contest type is different.')
        parser.add_argument('-f', '--no-fsanitize', action='store_true', default=False,
                             help='do not use sanitizers for ingen and inwer programs')
        parser.add_argument('-n', '--no-validate', default=False, action='store_true',
                            help='do not validate test contents')
        parsers.add_cpus_argument(parser, 'number of cpus that sinol-make will use')
        parser.add_argument('--ignore-expected', dest='ignore_expected', action='store_true',
                            help='ignore expected scores from config.yml. When this flag is set, '
                                 'the expected scores are not compared with the actual scores. '
                                 'This flag will be passed to the run command.')
        parsers.add_compilation_arguments(parser)

    def correct_contest_type(self):
        if self.args.expected_contest_type is not None:
            if self.contest.get_type() != self.args.expected_contest_type.lower():
                util.exit_with_error(f"Invalid contest type '{self.contest.get_type()}'. "
                                     f"Expected '{self.args.expected_contest_type}'.")

    def remove_cache(self):
        """
        Remove whole cache dir, but keep the directories.
        """
        cache_dir = paths.get_cache_path()
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
        cache.create_cache_dirs()

    def check_extra_files(self):
        """
        Checks if extra_compilation_files and extra_execution_files exist.
        """
        extra_compilation_files = self.config.get('extra_compilation_files', [])
        for file in extra_compilation_files:
            if not os.path.exists(os.path.join(os.getcwd(), "prog", file)):
                util.exit_with_error(f"Extra compilation file `{file}` does not exist. "
                                     f"It should be in `prog` directory.")
        if extra_compilation_files:
            print(util.info("All extra compilation files exist."))

        extra_execution_files = self.config.get('extra_execution_files', {})
        for lang, files in extra_execution_files.items():
            for file in files:
                if not os.path.exists(os.path.join(os.getcwd(), "prog", file)):
                    util.exit_with_error(f"Extra execution file `{file}` for language `{lang}` does not exist. "
                                         f"It should be in `prog` directory.")
        if extra_execution_files:
            print(util.info("All extra execution files exist."))

    def verify_scores(self, scored_groups):
        config_scores = self.config.get('scores', {})
        if not config_scores:
            return
        if '0' in scored_groups:
            scored_groups.remove('0')
        if 0 in scored_groups:
            scored_groups.remove(0)

        for group in scored_groups:
            if int(group) not in config_scores:
                util.exit_with_error(f"Score for group '{group}' not found. "
                                     f"You must either provide scores for all groups "
                                     f"or not provide them at all (to have them assigned automatically).")

        for group in config_scores:
            if int(group) not in scored_groups:
                util.exit_with_error(f"Score for group '{group}' found in config, "
                                     f"but no such test group exists in scored groups. "
                                     f"You must either provide scores for all groups "
                                     f"or not provide them at all (to have them assigned automatically).")

        print(util.info("All scores are provided for all groups."))

    def prepare_args(self, command):
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='command')
        command_parser = command.configure_subparser(subparser)
        command_args = command_parser.parse_args([])
        for key, value in vars(self.args).items():
            setattr(command_args, key, value)
        setattr(command_args, 'fsanitize', not self.args.no_fsanitize)
        return command_args

    def run_stresstests(self):
        stresstests_path = os.path.join(os.getcwd(), 'prog', self.task_id + 'stresstest.sh')
        if not os.path.exists(stresstests_path):
            return

        print(util.bold(' Running stress tests '.center(util.get_terminal_size()[1], '=')))
        print(f"See the comments in `prog/{self.task_id}stresstest.sh` for details.".center(
            util.get_terminal_size()[1], ' '))
        st = os.stat(stresstests_path)
        os.chmod(stresstests_path, st.st_mode | stat.S_IEXEC)
        p = subprocess.Popen([stresstests_path], shell=True)
        p.wait()
        if p.returncode != 0:
            util.exit_with_error("Stress tests failed.")

    def run(self, args: argparse.Namespace):
        self.args = util.init_package_command(args)
        self.config = package_util.get_config()
        self.task_id = package_util.get_task_id()
        self.contest = contest_types.get_contest_type()

        self.correct_contest_type()
        self.remove_cache()
        self.check_extra_files()
        self.contest.verify_pre_gen()

        # Run stresstests (if present)
        self.run_stresstests()

        # Generate tests
        print(util.bold(' Generating tests '.center(util.get_terminal_size()[1], '=')))
        gen = GenCommand()
        gen.run(self.prepare_args(gen))
        self.verify_scores(package_util.get_groups(package_util.get_all_inputs(self.task_id), self.task_id))

        # Generate problem statements
        print(util.bold(' Generating problem statements '.center(util.get_terminal_size()[1], '=')))
        doc = DocCommand()
        doc.run(self.prepare_args(doc))

        # Run inwer
        if inwer_util.get_inwer_path(self.task_id) is None:
            print(util.warning("Package doesn't have inwer."))
        else:
            print(util.bold(' Running inwer '.center(util.get_terminal_size()[1], '=')))
            inwer = InwerCommand()
            inwer.run(self.prepare_args(inwer))

        # Run solutions
        print(util.bold(' Running solutions '.center(util.get_terminal_size()[1], '=')))
        run = RunCommand()
        run.run(self.prepare_args(run))

        print(util.info('Package verification successful.'))
