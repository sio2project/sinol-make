import os
import subprocess
import sys
import shutil
import tarfile
import tempfile
import requests

from sinol_make import util
from sinol_make.executors.sio2jail import Sio2jailExecutor
from sinol_make.structs.status_structs import Status

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

    executor = Sio2jailExecutor(get_default_sio2jail_path())
    test_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'perf_test.py')
    python_executable = sys.executable
    command = [python_executable, test_file]
    time_limit = 1000
    memory_limit = 65536

    with (
        tempfile.NamedTemporaryFile() as sio2jail_result,
        tempfile.TemporaryFile() as command_stdout,
        tempfile.TemporaryFile() as command_stderr
    ):
        result = executor.execute(
            command=command,
            time_limit=time_limit,
            hard_time_limit=None,
            memory_limit=memory_limit,
            result_file_path=sio2jail_result.name,
            executable=None,
            execution_dir=None,
            stdout=command_stdout,
            stderr=command_stderr)
        command_stdout.seek(0)
        output_str = command_stdout.read().decode('utf-8')
        command_stderr.seek(0)
        error_str = command_stderr.read().decode('utf-8')
        sio2jail_result.seek(0)
        result_raw = sio2jail_result.read().decode('utf-8')

    expected_output = "Test Successful!\n"
    if result.Status != Status.OK or output_str != expected_output or error_str:
        max_perf_event_paranoid = 2
        if perf_event_paranoid > max_perf_event_paranoid:
            hint = (f"You have sysctl kernel.perf_event_paranoid = {perf_event_paranoid}"
                "\nThis might restrict access to instruction counting."
                "\nTry relaxing this setting by running:"
                f"\n\tsudo sysctl kernel.perf_event_paranoid={max_perf_event_paranoid}"
                "\nIf that fixes the problem, you can set this permanently by adding:"
                f"\n\tkernel.perf_event_paranoid={max_perf_event_paranoid}"
                "\nto /etc/sysctl.conf and rebooting."
            )
        else:
            hint = ("Your kernel, drivers, or hardware might be unsupported."
                "\nDiagnose this further by trying the following commands:"
                "\n1. Check if the `perf` tool is able to read performance counters correctly:"
                "\n\tperf stat -e instructions:u -- sleep 0"
                "\nIf `perf` can't be found, it might be located in: /usr/lib/linux-tools/*/perf"
                "\n2. Check if the Performance Monitoring Unit driver was successfully loaded:"
                "\n\tdmesg | grep PMU"
            )
        opt_stdout_hint = f"\nCommand stdout (expected {repr(expected_output)}):\n---\n{output_str}" if output_str != expected_output else ""
        opt_stderr_hint = f"\nCommand stderr (expected none):\n---\n{error_str}" if error_str else ""
        opt_sio2jail_hint = f"\nsio2jail result:\n---\n{result_raw}" if result.Status != Status.OK else ""
        util.exit_with_error("Failed sio2jail instruction counting self-check!"
            f"\n\nTest command:\n---\n{result.Cmdline}\n"
            f"{opt_stdout_hint}"
            f"{opt_stderr_hint}"
            f"{opt_sio2jail_hint}"
            f"\n\n{hint}"
            "\n\nYou can also disable instruction counting by adding the `--time-tool time` flag."
            "\nThis will make measured solution run times significantly different from SIO2."
            "\nFor more details, see https://github.com/sio2project/sio2jail#running."
        )
