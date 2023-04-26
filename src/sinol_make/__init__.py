import argparse
from sinol_make.util import get_commands

def main():
	parser = argparse.ArgumentParser(
		prog='sinol-make',
		description='Tool for creating and testing sio2 tasks',
	)
	subparsers = parser.add_subparsers(
		title='commands',
		description='sinol-make commands',
		dest='command',
	)
	subparsers.required = False

	commands = get_commands()

	for command in commands:
		command.configure_subparser(subparsers)

	args = parser.parse_args()

	for command in commands:
		if command.get_name() == args.command:
			command.run(args)
			exit(0)

	parser.print_help()
