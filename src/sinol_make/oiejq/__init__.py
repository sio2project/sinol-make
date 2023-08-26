import os
import subprocess
import sys
import tarfile
import tempfile
import requests

from sinol_make import util


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
            p.kill()
            return p.returncode == 0
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

    # oiejq is downloaded to a temporary directory and not to the `cache` dir,
    # as there is no guarantee that the current directory is the package directory.
    # The `cache` dir is only used for files that are part of the package and those
    # that the package creator might want to look into.
    with tempfile.TemporaryDirectory() as tmpdir:
        oiejq_path = os.path.join(tmpdir, 'oiejq.tar.gz')
        with open(oiejq_path, 'wb') as oiejq_file:
            oiejq_file.write(request.content)

        def strip(tar):
            l = len('oiejq/')
            for member in tar.getmembers():
                member.name = member.name[l:]
                yield member

        with tarfile.open(oiejq_path) as tar:
            tar.extractall(path=os.path.expanduser('~/.local/bin'), members=strip(tar))
        os.rename(os.path.expanduser('~/.local/bin/oiejq.sh'), os.path.expanduser('~/.local/bin/oiejq'))

    return check_oiejq()


def get_oiejq_path():
    if not check_oiejq():
        return None

    def check(path):
        p = subprocess.Popen([path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        p.kill()
        if p.returncode == 0:
            return True
        else:
            return False

    if check(os.path.expanduser('~/.local/bin/oiejq')):
        return os.path.expanduser('~/.local/bin/oiejq')
    else:
        return None


def check_perf_counters_enabled():
    """
    Checks if `kernel.perf_event_paranoid` is set to -1.
    :return:
    """
    if sys.platform != 'linux' or not check_oiejq():
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
