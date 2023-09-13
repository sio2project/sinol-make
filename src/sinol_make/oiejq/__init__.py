import os
import subprocess
import sys
import shutil
import tarfile
import tempfile
import requests

from sinol_make import util


def _check_if_oiejq_executable(path):
    if not os.access(path, os.X_OK):
        return False

    try:
        p = subprocess.Popen([path], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        return p.returncode == 0
    except FileNotFoundError:
        return False


def check_oiejq(path = None):
    """
    Function to check if oiejq is installed
    """
    if not util.is_linux():
        return False

    if path is not None:
        return _check_if_oiejq_executable(path)

    if _check_if_oiejq_executable(os.path.expanduser('~/.local/bin/oiejq')):
        return True
    else:
        return False


def install_oiejq():
    """
    Function to install oiejq, if not installed.
    Returns True if successful.
    """
    if not util.is_linux():
        return False
    if check_oiejq():
        return True

    if not os.path.exists(os.path.expanduser('~/.local/bin')):
        os.makedirs(os.path.expanduser('~/.local/bin'), exist_ok=True)

    if os.path.exists(os.path.expanduser('~/.local/bin/oiejq')) and \
            not _check_if_oiejq_executable(os.path.expanduser('~/.local/bin/oiejq')):
        util.exit_with_error("Couldn't install `oiejq`.\n"
                        "There is a file/directory named `oiejq` in `~/.local/bin` which isn't an `oiejq` executable.\n"
                        "Please rename it or remove it and try again.")

    try:
        request = requests.get('https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz')
    except requests.exceptions.ConnectionError:
        raise Exception('Couldn\'t download oiejq (https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz couldn\'t connect)')
    if request.status_code != 200:
        raise Exception('Couldn\'t download oiejq (https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz returned status code: ' + str(request.status_code) + ')')

    # oiejq is downloaded to a temporary directory and not to the `.cache` dir,
    # as there is no guarantee that the current directory is the package directory.
    # The `.cache` dir is only used for files that are part of the package and those
    # that the package creator might want to look into.
    with tempfile.TemporaryDirectory() as tmpdir:
        oiejq_path = os.path.join(tmpdir, 'oiejq.tar.gz')
        with open(oiejq_path, 'wb') as oiejq_file:
            oiejq_file.write(request.content)

        with tarfile.open(oiejq_path) as tar:
            tar.extractall(path=tmpdir)
        shutil.copy(os.path.join(tmpdir, 'oiejq', 'oiejq.sh'), os.path.expanduser('~/.local/bin/oiejq'))
        shutil.copy(os.path.join(tmpdir, 'oiejq', 'sio2jail'), os.path.expanduser('~/.local/bin/'))

    return check_oiejq()


def get_oiejq_path():
    if _check_if_oiejq_executable(os.path.expanduser('~/.local/bin/oiejq')):
        return os.path.expanduser('~/.local/bin/oiejq')
    else:
        return None


def check_perf_counters_enabled():
    """
    Checks if `kernel.perf_event_paranoid` is set to -1.
    :return:
    """
    if not util.is_linux() or not check_oiejq():
        return

    oiejq = get_oiejq_path()
    test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'perf_test.py')
    python_executable = sys.executable

    # subprocess.Pipe is not used, because than the code would hang on process.communicate()
    with tempfile.TemporaryFile() as tmpfile:
        process = subprocess.Popen([oiejq, python_executable, test_file], stdout=tmpfile, stderr=subprocess.DEVNULL)
        process.wait()
        tmpfile.seek(0)
        output = tmpfile.read().decode('utf-8')
        process.terminate()

    if output != "Test string\n":
        util.exit_with_error("To use the recommended tool for measuring time called oiejq, please:\n"
                             "- execute `sudo sysctl kernel.perf_event_paranoid=-1` to make oiejq work for\n"
                             "  the current system session,\n"
                             "- or add `kernel.perf_event_paranoid=-1` to `/etc/sysctl.conf`\n"
                             "  and reboot to permanently make oiejq work.\n"
                             "For more details, see https://github.com/sio2project/sio2jail#running.\n")
