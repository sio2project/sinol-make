import tempfile, shutil
from ...util import *
from .util import *
from sinol_make import configure_parsers

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
