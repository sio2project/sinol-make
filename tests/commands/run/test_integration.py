import tempfile, shutil, yaml, pytest
from ...util import *
from .util import *
from sinol_make import configure_parsers

def test_simple():
	"""
	Test a simple run.
	"""
	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)
		os.chdir(package_path)

		command = get_command()
		create_ins_outs(package_path, command)

		parser = configure_parsers()

		args = parser.parse_args(["run"])
		command = Command()
		command.run(args)


def test_no_expected_scores(capsys):
	"""
	Test with no sinol_expected_scores in config.yml.
	Should run, but exit with exit code 1.
	"""
	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)
		os.chdir(package_path)

		command = get_command()
		create_ins_outs(package_path, command)

		config_path = os.path.join(package_path, "config.yml")
		config = yaml.load(open(config_path, "r"), Loader=yaml.SafeLoader)
		del config["sinol_expected_scores"]
		open(config_path, "w").write(yaml.dump(config))

		parser = configure_parsers()
		args = parser.parse_args(["run"])
		command = Command()
		with pytest.raises(SystemExit) as e:
			command.run(args)

		assert e.type == SystemExit
		assert e.value.code == 1

		out = capsys.readouterr().out
		assert "Solutions were added:" in out
		assert "abc.cpp" in out


def test_apply_suggestions():
	"""
	Test with no sinol_expected_scores in config.yml.
	Verifies that suggestions are applied.
	"""

	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)
		os.chdir(package_path)

		command = get_command()
		create_ins_outs(package_path, command)

		config_path = os.path.join(package_path, "config.yml")
		config = yaml.load(open(config_path, "r"), Loader=yaml.SafeLoader)
		expected_scores = config["sinol_expected_scores"]
		del config["sinol_expected_scores"]
		open(config_path, "w").write(yaml.dump(config))

		parser = configure_parsers()
		args = parser.parse_args(["run", "--apply_suggestions"])
		command = Command()
		command.run(args)

		config = yaml.load(open(config_path, "r"), Loader=yaml.SafeLoader)
		assert config["sinol_expected_scores"] == expected_scores


def test_incorrect_expected_scores(capsys):
	"""
	Test with incorrect sinol_expected_scores in config.yml.
	"""

	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)
		os.chdir(package_path)

		command = get_command()
		create_ins_outs(package_path, command)

		config_path = os.path.join(package_path, "config.yml")
		config = yaml.load(open(config_path, "r"), Loader=yaml.SafeLoader)
		config["sinol_expected_scores"]["abc.cpp"]["expected"][1] = "WA"
		config["sinol_expected_scores"]["abc.cpp"]["points"] = 75
		open(config_path, "w").write(yaml.dump(config))

		parser = configure_parsers()
		args = parser.parse_args(["run"])
		command = Command()

		with pytest.raises(SystemExit) as e:
			command.run(args)

		out = capsys.readouterr().out

		assert e.type == SystemExit
		assert e.value.code == 1
		assert "Solution abc.cpp passed group 1 with status OK while it should pass with status WA." in out


def test_flag_tests(capsys):
	"""
	Test flag --tests.
	"""

	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)
		os.chdir(package_path)

		command = get_command()
		create_ins_outs(package_path, command)

		parser = configure_parsers()
		args = parser.parse_args(["run", "--tests", "in/abc1a.in"])
		command = Command()
		command.run(args)

		out = capsys.readouterr().out

		assert command.tests == ["in/abc1a.in"]


def test_flag_programs(capsys):
	"""
	Test flag --programs.
	"""

	with tempfile.TemporaryDirectory() as tmpdir:
		package_path = os.path.join(tmpdir, "abc")
		shutil.copytree(get_simple_package_path(), package_path)
		os.chdir(package_path)

		command = get_command()
		create_ins_outs(package_path, command)

		parser = configure_parsers()
		args = parser.parse_args(["run", "--programs", "prog/abc1.cpp", "prog/abc2.cpp"])
		command = Command()
		command.run(args)

		out = capsys.readouterr().out

		assert "abc1.cpp" in out
		assert "abc2.cpp" in out
		assert "abc3.cpp" not in out
