import tempfile, shutil, yaml, glob
import multiprocessing as mp
from sinol_make.helpers import compiler
from sinol_make import configure_parsers
from sinol_make import util
from sinol_make.commands.run import Command
from ..util import *

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


def test_get_programs():
	command = get_command()
	programs = command.get_programs(None)
	assert programs == ["abc.cpp", "abc1.cpp", "abc2.cpp", "abc3.cpp", "abc4.cpp"]


def test_compile_programs():
	with tempfile.TemporaryDirectory() as tmpdir:
		shutil.copytree(get_simple_package_path(), os.path.join(tmpdir, "abc"))

		command = get_command(os.path.join(tmpdir, "abc"))
		programs = command.get_programs(None)
		result = command.compile_programs(programs)
		assert result == [True for _ in programs]


def test_get_tests():
	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)

		command = get_command(package_path)
		create_ins(package_path, command)
		os.chdir(package_path)
		tests = command.get_tests(None)
		assert tests == ["in/abc1a.in", "in/abc2a.in", "in/abc3a.in", "in/abc4a.in"]


def test_execution():
	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)

		command = get_command(package_path)
		program = "abc.e"
		result = command.compile_programs([program])
		assert result == [True]

		create_ins(package_path, command)
		os.chdir(package_path)
		create_outs(package_path, command)
		os.chdir(package_path)
		test = command.get_tests(None)[0]

		config = yaml.load(open(os.path.join(package_path, "config.yml"), "r"), Loader=yaml.FullLoader)

		os.makedirs(os.path.join(command.EXECUTIONS_DIR, program), exist_ok=True)
		result = command.execute((program, os.path.join(command.EXECUTABLES_DIR, program), test, config['time_limit'], config['memory_limit'], util.get_oiejq_path()))
		assert result["Status"] == "OK"


def test_run_simple():
	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)

		command = get_command()
		create_ins(package_path, command)
		os.chdir(package_path)
		create_outs(package_path, command)
		os.chdir(package_path)

		parser = configure_parsers()

		args = parser.parse_args(["run"])
		command = Command()
		command.run(args)
