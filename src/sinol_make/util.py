import glob, importlib, os, sys, subprocess, requests, tarfile, yaml

def get_commands():
	"""
	Function to get an array of all available commands.
	"""
	commands_path = glob.glob(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'commands/*'
        )
	)
	commands = []
	for path in commands_path:
		temp = importlib.import_module('sinol_make.commands.' + os.path.basename(path), 'Command')
		commands.append(temp.Command())

	return commands


def check_if_project():
	"""
	Function to check if current directory is a project
	"""

	cwd = os.getcwd()
	if os.path.exists(os.path.join(cwd, 'config.yml')):
		return True
	return False


def check_oiejq(path = None):
	"""
	Function to check if oiejq is installed
	"""
	if sys.platform != 'linux':
		return False

	def check(path):
		try:
			p = subprocess.Popen([path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			p.wait()
			if p.returncode == 0:
				return True
			else:
				return False
		except FileNotFoundError:
			return False

	if path is not None:
		return check(path)

	if not check(os.path.expanduser('~/.local/bin/oiejq')):
		return False
	else:
		return True


def install_oiejq():
	"""
	Function to install oiejq, if not installed.
	Returns True if successful.
	"""

	if sys.platform != 'linux':
		return False
	if check_oiejq():
		return True

	if not os.path.exists(os.path.expanduser('~/.local/bin')):
		os.makedirs(os.path.expanduser('~/.local/bin'), exist_ok=True)

	try:
		request = requests.get('https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz')
	except requests.exceptions.ConnectionError:
		raise Exception('Couldn\'t download oiejq (https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz couldn\'t connect)')
	if request.status_code != 200:
		raise Exception('Couldn\'t download oiejq (https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz returned status code: ' + str(request.status_code) + ')')
	open('/tmp/oiejq.tar.gz', 'wb').write(request.content)

	def strip(tar):
		l = len('oiejq/')
		for member in tar.getmembers():
			member.name = member.name[l:]
			yield member

	tar = tarfile.open('/tmp/oiejq.tar.gz')
	tar.extractall(path=os.path.expanduser('~/.local/bin'), members=strip(tar))
	tar.close()
	os.remove('/tmp/oiejq.tar.gz')
	os.rename(os.path.expanduser('~/.local/bin/oiejq.sh'), os.path.expanduser('~/.local/bin/oiejq'))

	return check_oiejq()


def get_oiejq_path():
	if not check_oiejq():
		return None

	def check(path):
		p = subprocess.Popen([path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p.wait()
		if p.returncode == 0:
			return True
		else:
			return False

	if check(os.path.expanduser('~/.local/bin/oiejq')):
		return os.path.expanduser('~/.local/bin/oiejq')
	else:
		return None


def save_config(config):
	"""
	Function to save nicely formated config.yml.
	"""

	# We add the fields in the `config.yml`` in a particular order to make the config more readable.
	# The fields that are not in this list will be appended to the end of the file.
	order = [
		"title",
		"title_pl",
		"title_en",
		"memory_limit",
		"memory_limits",
		"time_limit",
		"time_limits",
		"override_limits",
		"scores",
		"extra_compilation_files",
		{
			"key": "sinol_expected_scores",
			"default_flow_style": None
		}
	]

	config = config.copy()
	with open("config.yml", "w") as config_file:
		for field in order:
			if isinstance(field, dict): # If the field is a dict, it means that it has a custom property (for example default_flow_style).
				if field["key"] in config:
					yaml.dump({field["key"]: config[field["key"]]}, config_file, default_flow_style=field["default_flow_style"])
					# The considered fields are deleted, thus `config` at the end will contain only custom fields written by the user.
					del config[field["key"]]
			else: # When the field is a string, it doesn't have any custom properties, so it's just a dict key.
				if field in config:
					yaml.dump({field: config[field]}, config_file)
					del config[field] # Same reason for deleting as above.

		if config != {}:
			print(warning("Found unknown fields in config.yml: " + ", ".join([str(x) for x in config])))
			# All remaining non-considered fields are appended to the end of the file.
			yaml.dump(config, config_file)


def color_red(text): return "\033[91m{}\033[00m".format(text)
def color_green(text): return "\033[92m{}\033[00m".format(text)
def color_yellow(text): return "\033[93m{}\033[00m".format(text)
def bold(text): return "\033[01m{}\033[00m".format(text)

def info(text):
	return bold(color_green(text))
def warning(text):
	return bold(color_yellow(text))
def error(text):
	return bold(color_red(text))

def exit_with_error(text):
	print(error(text))
	exit(1)
