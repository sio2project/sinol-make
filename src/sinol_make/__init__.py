import argparse
from sinol_make import util

def configure_parsers():
	parser = argparse.ArgumentParser(
		prog='sinol-make',
		description='Tool for creating and testing sio2 tasks',
	)
	parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.0.1")
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
			command.run(args)
			exit(0)

	parser.print_help()
