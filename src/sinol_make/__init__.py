# PYTHON_ARGCOMPLETE_OK
import sys
import argparse
import traceback
import argcomplete

from sinol_make import util, sio2jail
from sinol_make.helpers import cache, oicompare

# Required for side effects
from sinol_make.task_type.normal import NormalTaskType # noqa
from sinol_make.task_type.interactive import InteractiveTaskType # noqa


__version__ = "1.9.5"


def configure_parsers():
    parser = argparse.ArgumentParser(
        prog='sinol-make',
        description='Tool for creating and testing sio2 tasks',
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + __version__)
    subparsers = parser.add_subparsers(
        title='command',
        description='sinol-make commands',
        dest='command',
    )
    subparsers.required = False

    commands = util.get_commands()

    for command in commands:
        command.configure_subparser(subparsers)

    argcomplete.autocomplete(parser)
    return parser


def check_sio2jail():
    if sio2jail.sio2jail_supported() and not sio2jail.check_sio2jail():
        print(util.warning('Up to date `sio2jail` in `~/.local/bin/` not found, installing new version...'))
        try:
            if sio2jail.install_sio2jail():
                print(util.info('Newest `sio2jail` was successfully installed.'))
            else:
                util.exit_with_error('`sio2jail` could not be installed.\n'
                                     'You can download it from https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz '
                                     'and unpack it to `~/.local/bin/`.\n'
                                     'You can also use --sio2jail-path to specify path to your sio2jail.')
        except Exception as err:
            util.exit_with_error('`sio2jail` could not be installed.\n' + str(err))


def main_exn():
    parser = configure_parsers()
    arguments = []
    curr_args = []
    commands = util.get_commands()
    commands_dict = {command.get_name(): command for command in commands}
    commands_short_dict = {command.get_short_name(): command for command in commands if command.get_short_name()}
    for arg in sys.argv[1:]:
        if arg in commands_dict.keys() and not (len(curr_args) > 0 and curr_args[0] == 'init'):
            if curr_args:
                arguments.append(curr_args)
            curr_args = [arg]
        elif arg in commands_short_dict.keys() and not (len(curr_args) > 0 and curr_args[0] == 'init'):
            if curr_args:
                arguments.append(curr_args)
            curr_args = [commands_short_dict[arg].get_name()]
        else:
            curr_args.append(arg)
    if curr_args:
        arguments.append(curr_args)
    if not arguments:
        parser.print_help()
        exit(1)
    check_sio2jail()
    oicompare.check_and_download()

    for curr_args in arguments:
        args = parser.parse_args(curr_args)
        command = commands_dict.get(args.command, None)
        if command:
            if len(arguments) > 1:
                print(f' {command.get_name()} command '.center(util.get_terminal_size()[1], '='))
            command.run(args)
        else:
            parser.print_help()
            exit(1)


def main():
    new_version = None
    try:
        if util.is_dev(__version__):
            print(util.warning('You are using a development version of sinol-make. '
                               'It may be unstable and contain bugs.'))
        new_version = util.check_for_updates(__version__)
        main_exn()
    except argparse.ArgumentError as err:
        util.exit_with_error(err)
    except SystemExit as err:
        exit(err.code)
    except Exception:
        print(traceback.format_exc())
        util.exit_with_error('An error occurred while running the command.\n'
                             'If that is a bug, please report it or submit a bugfix: '
                             'https://github.com/sio2project/sinol-make/#reporting-bugs-and-contributing-code')
    finally:
        if new_version is not None:
            if not util.is_dev(new_version):
                print(util.warning(
                    f'New version of sinol-make is available (your version: {__version__}, available version: '
                    f'{new_version}).\n'
                    f'Changelog can be found at https://github.com/sio2project/sinol-make/releases.\n'
                    f'You can update sinol-make by running `pip install sinol-make --upgrade`.'))
            elif util.is_dev(new_version):
                print(util.warning(
                    f'New development version of sinol-make is available (your version: {__version__}, available '
                    f'version: {new_version}).\n'
                    f'Changelog can be found at https://github.com/sio2project/sinol-make/releases.\n'
                    f'You can update sinol-make by running `pip install sinol-make --pre --upgrade`.'
                ))
