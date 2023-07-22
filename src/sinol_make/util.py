import glob, importlib, os, sys, subprocess, requests, tarfile, yaml
import importlib.resources
import threading


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


def check_for_updates(current_version) -> str | None:
    """
    Function to check if there is a new version of sinol-make.
    :param current_version: current version of sinol-make
    :return: returns new version if there is one, None otherwise
    """
    data_dir = importlib.resources.files("sinol_make").joinpath("data")
    if not data_dir.is_dir():
        os.mkdir(data_dir)

    # We check for new version asynchronously, so that it doesn't slow down the program.
    thread = threading.Thread(target=check_version)
    thread.start()
    version_file = data_dir.joinpath("version")

    if version_file.is_file():
        version = version_file.read_text()
        try:
            if compare_versions(current_version, version) == -1:
                return version
            else:
                return None
        except ValueError:  # If the version file is corrupted, we just ignore it.
            return None
    else:
        return None


def check_version():
    """
    Function that asynchronously checks for new version of sinol-make.
    Writes the newest version to data/version file.
    """
    try:
        request = requests.get("https://pypi.python.org/pypi/sinol-make/json", timeout=1)
    except requests.exceptions.RequestException:
        return

    if request.status_code != 200:
        return

    data = request.json()
    latest_version = data["info"]["version"]

    version_file = importlib.resources.files("sinol_make").joinpath("data/version")
    version_file.write_text(latest_version)


def compare_versions(version_a, version_b):
    """
    Function to compare two versions.
    Returns 1 if version_a > version_b, 0 if version_a == version_b, -1 if version_a < version_b.
    """

    def convert(version):
        return tuple(map(int, version.split(".")))

    version_a = convert(version_a)
    version_b = convert(version_b)

    if version_a > version_b:
        return 1
    elif version_a == version_b:
        return 0
    else:
        return -1


def lines_diff(lines1, lines2):
    """
    Function to compare two lists of lines.
    Returns True if they are the same, False otherwise.
    """
    if len(lines1) != len(lines2):
        return False

    for i in range(len(lines1)):
        if lines1[i].rstrip() != lines2[i].rstrip():
            return False

    return True


def file_diff(file1, file2):
    """
    Function to compare two files.
    Returns True if they are the same, False otherwise.
    """
    return lines_diff(open(file1).readlines(), open(file2).readlines())


def get_terminal_size():
    """
    Function to get the size of the terminal.
    :return: triple (has_terminal, width, height)
    """
    has_terminal = True
    try:
        terminal_width = os.get_terminal_size().columns
        terminal_height = os.get_terminal_size().lines
    except OSError:
        has_terminal = False
        terminal_width = 80
        terminal_height = 30
    return has_terminal, terminal_width, terminal_height

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
