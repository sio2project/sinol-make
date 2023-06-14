import argparse
import sys

from sinol_make import util

__version__ = "1.0.0"

def configure_parsers():
	parser = argparse.ArgumentParser(
		prog='sinol-make',
		description='Tool for creating and testing sio2 tasks',
	)
	parser.add_argument("-v", "--version", action="version", version="%(prog)s " + __version__)
	subparsers = parser.add_subparsers(
		title='commands',
		description='sinol-make commands',
		dest='command',
	)
	subparsers.required = False

	commands = util.get_commands()

	for command in commands:
		command.configure_subparser(subparsers)
	return parser


def main():
	parser = configure_parsers()
	commands = util.get_commands()
	args = parser.parse_args()

	for command in commands:
		if command.get_name() == args.command:
			if sys.platform == 'linux' and not util.check_oiejq():
				print(util.warning('`oiejq` is not installed. It will be installed now.'))

				try:
					if util.install_oiejq():
						print(util.info('`oiejq` was successfully installed.'))
					else:
						print(util.error('`oiejq` could not be installed. You can try installing it manually.'))
						exit(1)
				except Exception as e:
					print(util.error('`oiejq` could not be installed.'))
					print(util.error(e))
					exit(1)

			command.run(args)
			exit(0)

	parser.print_help()
