import os
import subprocess
import sys
import shutil
import tarfile
import tempfile
import requests

from sinol_make import util


def sio2jail_supported():
    return util.is_linux()


def get_default_sio2jail_path():
    return os.path.expanduser('~/.local/bin/sio2jail')


def check_sio2jail(path=None):
    if path is None:
        path = get_default_sio2jail_path()
    try:
        sio2jail = subprocess.Popen([path, "--version"],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = sio2jail.communicate()
        out = out.decode(sys.stdout.encoding)
        if not out.startswith("SIO2jail v1.5.0 "):
            return False
    except FileNotFoundError:
        return False
    return True


def install_sio2jail(directory=None):
    """
    Downloads and installs sio2jail to the specified directory, creating it if it doesn't exist
    """
    if directory is None:
        directory = os.path.expanduser('~/.local/bin')
    path = os.path.join(directory, 'sio2jail')
    if os.path.exists(path) and check_sio2jail(path):
        return

    print(util.warning(f'`sio2jail` not found in `{path}`, attempting download...'))

    os.makedirs(directory, exist_ok=True)

    url = 'https://oij.edu.pl/zawodnik/srodowisko/oiejq.tar.gz'
    try:
        request = requests.get(url)
    except requests.exceptions.ConnectionError:
        util.exit_with_error('Couldn\'t download sio2jail ({url} couldn\'t connect)')
    if request.status_code != 200:
        util.exit_with_error('Couldn\'t download sio2jail ({url} returned status code: ' + str(request.status_code) + ')')

    # oiejq is downloaded to a temporary directory and not to the `.cache` dir,
    # as there is no guarantee that the current directory is the package directory.
    # The `.cache` dir is only used for files that are part of the package and those
    # that the package creator might want to look into.
    with tempfile.TemporaryDirectory() as tmpdir:
        oiejq_path = os.path.join(tmpdir, 'oiejq.tar.gz')
        with open(oiejq_path, 'wb') as oiejq_file:
            oiejq_file.write(request.content)

        with tarfile.open(oiejq_path) as tar:
            util.extract_tar(tar, tmpdir)
        shutil.copy(os.path.join(tmpdir, 'oiejq', 'sio2jail'), directory)

    check_sio2jail(path)
    print(util.info(f'`sio2jail` was successfully installed in `{path}`'))
    return True


def check_perf_counters_enabled():
    """
    Checks if sio2jail is able to use perf counters to count instructions.
    """
    if not sio2jail_supported() or not check_sio2jail():
        return

    with open('/proc/sys/kernel/perf_event_paranoid') as f:
        perf_event_paranoid = int(f.read())

    sio2jail = get_default_sio2jail_path()
    test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'perf_test.py')
    python_executable = sys.executable

    # subprocess.Pipe is not used, because than the code would hang on process.communicate()
    with tempfile.TemporaryFile() as tmpfile:
        process = subprocess.Popen([sio2jail, '--mount-namespace', 'off', '--', python_executable, test_file],
                                   stdout=tmpfile, stderr=subprocess.DEVNULL)
        process.wait()
        tmpfile.seek(0)
        output = tmpfile.read().decode('utf-8')
        process.terminate()

    if output != "Test string\n":
        max_perf_event_paranoid = 2
        if perf_event_paranoid > max_perf_event_paranoid:
            hint = (f"You have `kernel.perf_event_paranoid` set to `{perf_event_paranoid}`"
                ", which might be preventing userspace perf counters from working.\n"
                f"Try running: `sudo sysctl kernel.perf_event_paranoid={max_perf_event_paranoid}`\n"
                "If that fixes the problem, you can set this permanently by adding "
                f"`kernel.perf_event_paranoid={max_perf_event_paranoid}` to `/etc/sysctl.conf` and rebooting.\n")
        else:
            hint = ("Your kernel, drivers, or hardware might be too old.\n"
                "Check if the Intel PMU driver is loaded: `dmesg | grep -i 'perf'`\n"
                "You can also check if the perf tool works correctly: `perf stat -e instructions:u -- sleep 0`\n"
                "(if perf can't be found, it might be located in: `/usr/lib/linux-tools/*/perf`).\n")
        cmdline = " ".join(process.args)
        util.exit_with_error(f"Failed performance counters test: `{cmdline}`\n"
            + hint +
            "Alternatively, you can run sinol-make without instruction counting"
            ", by adding the `--time-tool time` flag.\n"
            "For more details, see https://github.com/sio2project/sio2jail#running.\n")
