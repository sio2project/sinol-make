# PYTHON_ARGCOMPLETE_OK
import sys
import argparse
import traceback
import argcomplete

from sinol_make import util, oiejq

__version__ = "1.6.0.dev4"


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


def check_oiejq():
    if util.is_linux() and not oiejq.check_oiejq():
        print(util.warning('`oiejq` in `~/.local/bin/` not found, installing now...'))
        try:
            if oiejq.install_oiejq():
                print(util.info('`oiejq` was successfully installed.'))
            else:
                util.exit_with_error('`oiejq` could not be installed.\n'
                                     'You can download it from https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz, '
                                     'unpack it to `~/.local/bin/` and rename oiejq.sh to oiejq.\n'
                                     'You can also use --oiejq-path to specify path to your oiejq.')
        except Exception as err:
            util.exit_with_error('`oiejq` could not be installed.\n' + str(err))


def main_exn():
    parser = configure_parsers()
    arguments = []
    curr_args = []
    commands = util.get_commands()
    commands_dict = {command.get_name(): command for command in commands}
    for arg in sys.argv[1:]:
        if arg in commands_dict.keys() and not (len(curr_args) > 0 and curr_args[0] == 'init'):
            if curr_args:
                arguments.append(curr_args)
            curr_args = [arg]
        else:
            curr_args.append(arg)
    if curr_args:
        arguments.append(curr_args)
    if not arguments:
        parser.print_help()
        exit(1)
    check_oiejq()

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
                    f'{new_version}).\nYou can update it by running `pip3 install sinol-make --upgrade`.'))
            elif util.is_dev(new_version):
                print(util.warning(
                    f'New development version of sinol-make is available (your version: {__version__}, available '
                    f'version: {new_version}).\nYou can update it by running `pip3 install sinol-make --pre --upgrade`.'
                ))
