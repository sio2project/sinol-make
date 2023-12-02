import os
import sys
import tempfile
import subprocess

from sinol_make import util
from sinol_make.timetools.sio2jail import Sio2jailTimeTool


class Sio2jailCpuTimeTool(Sio2jailTimeTool):
    def get_name(self) -> str:
        return "sio2jail"

    def can_install(self) -> bool:
        return False

    def is_available(self) -> bool:
        if not util.is_linux() or not self.is_latest_version():
            return False

        test_file = os.path.join(os.path.realpath(__file__), 'perf_test.py')
        python_executable = sys.executable
        path = self.get_path()

        with tempfile.TemporaryFile() as tmpfile:
            process = subprocess.Popen([path, python_executable, test_file],
                                       stdout=tmpfile, stderr=subprocess.DEVNULL)
            process.wait()
            tmpfile.seek(0)
            output = tmpfile.read().decode('utf-8')
            process.terminate()

        if output != 'Test string\n':
            print(util.error("To use the recommended tool for measuring time called oiejq, please:\n"
                             "- execute `sudo sysctl kernel.perf_event_paranoid=-1` to make oiejq work for\n"
                             "  the current system session,\n"
                             "- or add `kernel.perf_event_paranoid=-1` to `/etc/sysctl.conf`\n"
                             "  and reboot to permanently make oiejq work.\n"
                             "For more details, see https://github.com/sio2project/sio2jail#running.\n"))
        return True

    def get_priority(self) -> int:
        return 10

    def _use_real_time(self) -> bool:
        return False
