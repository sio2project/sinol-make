import multiprocessing as mp
import os, glob
from ...util import *
from sinol_make.commands.run import Command
from sinol_make.helpers import compiler

def get_command(path = None):
	"""
	Helper to get a command object with the constants set.
	Changes dir to simple test package.
	"""
	if path is None:
		path = get_simple_package_path()
	command = Command()
	os.chdir(path)
	command.set_constants()
	command.cpus = mp.cpu_count()
	command.compilers = {
		'c_compiler_path': compiler.get_c_compiler_path(),
		'cpp_compiler_path': compiler.get_cpp_compiler_path(),
		'python_interpreter_path': compiler.get_python_interpreter_path(),
		'java_compiler_path': compiler.get_java_compiler_path()
	}
	return command

def create_ins(package_path, command):
	result = command.compile_programs(["abcingen.e"])
	assert result == [True]

	os.chdir(os.path.join(package_path, "in"))
	os.system("../cache/executables/abcingen.e")


def create_outs(package_path, command):
	result = command.compile_programs(["abc.e"])
	assert result == [True]

	os.chdir(os.path.join(package_path, "in"))
	for file in glob.glob("*.in"):
		os.system(f'{os.path.join(command.EXECUTABLES_DIR, "abc.e")} < {file} > ../out/{file.replace(".in", ".out")}')
