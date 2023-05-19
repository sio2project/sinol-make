import tempfile, shutil, yaml
from sinol_make import util
from .util import *
from ...util import *

def test_get_programs():
	command = get_command()
	solutions = command.get_solutions(None)
	assert solutions == ["abc.cpp", "abc1.cpp", "abc2.cpp", "abc3.cpp", "abc4.cpp"]


def test_compile_programs():
	with tempfile.TemporaryDirectory() as tmpdir:
		shutil.copytree(get_simple_package_path(), os.path.join(tmpdir, "abc"))

		command = get_command(os.path.join(tmpdir, "abc"))
		solutions = command.get_solutions(None)
		result = command.compile_solutions(solutions)
		assert result == [True for _ in solutions]


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
		solution = "abc.cpp"
		executable = command.get_executable(solution)
		result = command.compile_solutions([solution])
		assert result == [True]

		create_ins(package_path, command)
		os.chdir(package_path)
		create_outs(package_path, command)
		os.chdir(package_path)
		test = command.get_tests(None)[0]

		config = yaml.load(open(os.path.join(package_path, "config.yml"), "r"), Loader=yaml.FullLoader)

		os.makedirs(os.path.join(command.EXECUTIONS_DIR, solution), exist_ok=True)
		result = command.execute((solution, os.path.join(command.EXECUTABLES_DIR, executable), test, config['time_limit'], config['memory_limit'], util.get_oiejq_path()))
		assert result["Status"] == "OK"
