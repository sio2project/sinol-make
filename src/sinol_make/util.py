import glob, importlib, os, sys, subprocess, requests, tarfile

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


def check_oiejq():
	"""
	Function to check if oiejq is installed
	"""
	if sys.platform == 'win32' or sys.platform == 'darwin':
		return False
	
	def check(path):
		p = subprocess.Popen([path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		if p.returncode == 0:
			return True
		else:
			return False
		
	if not check('oiejq.sh') and not check(os.path.expanduser('~/.local/bin/oiejq.sh')):
		return False
	else:
		return True


def install_oiejq():
	"""
	Function to install oiejq, if not installed.
	Returns True if successful.
	"""
	
	if sys.platform == 'win32' or sys.platform == 'darwin':
		return False
	if check_oiejq():
		return True

	if not os.path.exists(os.path.expanduser('~/.local/bin')):
		os.makedirs(os.path.expanduser('~/.local/bin'))

	request = requests.get('https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz')
	if request.status_code != 200:
		raise Exception('Couldn\'t download oiejq (oij.edu.pl status code: ' + str(request.status_code) + ')')
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

	return check_oiejq()


def get_oiejq_path():
	if not check_oiejq():
		return None
	
	def check(path):
		p = subprocess.Popen([path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		if p.returncode == 0:
			return True
		else:
			return False
	
	if check('oiejq.sh'):
		return 'oiejq.sh'
	elif check(os.path.expanduser('~/.local/bin/oiejq.sh')):
		return os.path.expanduser('~/.local/bin/oiejq.sh')
	else:
		return None


def color_red(text): return "\033[91m{}\033[00m".format(text)
def color_green(text): return "\033[92m{}\033[00m".format(text)
def color_yellow(text): return "\033[93m{}\033[00m".format(text)
def bold(text): return "\033[01m{}\033[00m".format(text)