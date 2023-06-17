from random import choices
import sys

def pytest_addoption(parser):
	parser.addoption(
		'--time_tool',
		choices=['oiejq', 'time'],
		action='append',
		default=[],
		help='Time tool to use. Default: oiejq'
	)

def pytest_generate_tests(metafunc):
	if "time_tool" in metafunc.fixturenames:
		time_tools = []
		if metafunc.config.getoption("time_tool") != []:
			time_tools = metafunc.config.getoption("time_tool")
		elif sys.platform == "linux":
			time_tools = ["oiejq", "time"]
		else:
			time_tools = ["time"]
		metafunc.parametrize("time_tool", time_tools)
