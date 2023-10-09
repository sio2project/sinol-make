# PYTHON_ARGCOMPLETE_OK

import argcomplete
import traceback
import argparse
import sys
import os

from sinol_make import util, oiejq


__version__ = "1.5.12"


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


def main_exn():
    parser = configure_parsers()
    args = parser.parse_args()
    commands = util.get_commands()

    for command in commands:
        if command.get_name() == args.command:
            new_version = util.check_for_updates(__version__)
            if new_version is not None:
                print(util.warning(
                    f'New version of sinol-make is available (your version: {__version__}, available version: {new_version}).\n'
                    f' You can update it by running `pip3 install sinol-make --upgrade`.'))

            if util.is_linux() and not oiejq.check_oiejq():
                print(util.warning('`oiejq` in `~/.local/bin/` not found, installing now...'))

                try:
                    if oiejq.install_oiejq():
                        print(util.info('`oiejq` was successfully installed.'))
                    else:
                        util.exit_with_error('`oiejq` could not be installed.\n'
                                             'You can download it from https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz'
                                             ', unpack it to `~/.local/bin/` and rename oiejq.sh to oiejq.\n'
                                             'You can also use --oiejq-path to specify path to your oiejq.')
                except Exception as err:
                    util.exit_with_error('`oiejq` could not be installed.\n' + err)

            command.run(args)
            exit(0)

    parser.print_help()


def main():
    try:
        main_exn()
    except argparse.ArgumentError as err:
        util.exit_with_error(err)
    except SystemExit as err:
        exit(err.code)
    except:
        print(traceback.format_exc())
        util.exit_with_error('An error occurred while running the command.\n'
                             'If that is a bug, please report it or submit a bugfix: https://github.com/sio2project/sinol-make/#reporting-bugs-and-contributing-code')
