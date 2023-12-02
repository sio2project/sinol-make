from typing import List
import subprocess
import requests
import os

from sinol_make.structs.status_structs import Status
from sinol_make.structs.timetool_structs import TimeToolResult
from sinol_make.timetools.timetool import TimeTool
from sinol_make.timetools.utils import noquote


class Sio2jailTimeTool(TimeTool):
    INSTRUCTIONS_PER_VIRTUAL_SECOND = 2 * 10**9
    _supervisor_codes = {
        0: 'OK',
        120: 'OLE',
        121: 'RV',
        124: 'MLE',
        125: 'TLE'
    }

    _oiaug_codes = ['OK', 'RV', 'RE', 'TLE', 'MLE', 'OLE']

    def get_install_name(self) -> str:
        return "sio2jail"

    def get_path(self) -> str:
        return os.path.expanduser('~/.local/bin/sio2jail')

    def _use_real_time(self) -> bool:
        """
        :return: True if real time should be used.
        """
        raise NotImplementedError()

    def can_install(self) -> bool:
        return True

    def is_latest_version(self) -> bool:
        path = self.get_path()
        if not os.path.exists(path):
            return False
        process = subprocess.Popen([path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return False
        version = stdout.decode('utf-8').splitlines()[0].strip()
        return version == 'SIO2jail v1.4.4 compiled on Sep 13 2023 10:25:10 Linux 6.1.0-11-amd64 with gcc 12.2.0'

    def install(self):
        try:
            request = requests.get('https://github.com/sio2project/sio2jail/releases/download/v1.4.4/sio2jail')
        except requests.exceptions.ConnectionError:
            raise Exception("Couldn't download sio2jail (couldn't connect)")
        if request.status_code != 200:
            raise Exception("Couldn't download sio2jail (returned status code: " + str(request.status_code) + ")")

        with open(self.get_path(), 'wb') as f:
            f.write(request.content)
        os.chmod(self.get_path(), 0o755)

    def _get_arguments(self, args, time_limit, memory_limit, result_file_path) -> List[str]:
        options = ['--mount-namespace', 'off']
        options += ['-f', '3', '-s', '--memory-limit', str(memory_limit) + 'K']
        if self._use_real_time():
            options += ['--rtimelimit', str(time_limit) + 'ms']
            options += ['-o', 'oireal', '--perf', 'off']
        else:
            options += ['--instruction-count-limit', str(time_limit * self.INSTRUCTIONS_PER_VIRTUAL_SECOND // 1000)]
            options += ['--rtimelimit', str(2 * time_limit) + 'ms']

        args = [self.get_path()] + options + ['--'] + args + [noquote('3>'), result_file_path]
        return args

    def _supervisor_result_to_code(self, result):
        combined_code = int(result)
        result_code = self._supervisor_codes.get(combined_code, 'RE')
        exit_code = 0
        if combined_code > 200:
            exit_code = combined_code - 200
        elif result_code != 'OK':
            exit_code = -1
        return result_code, exit_code

    def _parse_result_file(self, result_file_path: str) -> TimeToolResult:
        with open(result_file_path, "r") as f:
            status_line = f.readline().strip().split()
            result_string = f.readline().strip()

        result_code = int(status_line[1])
        time_used = int(status_line[2])
        memory_used = int(status_line[4])
        num_syscalls = int(status_line[5])
        if result_string == 'ok':
            error = None
        else:
            error = result_string

        if status_line[0] in self._oiaug_codes:
            return TimeToolResult(
                status=Status.from_str(status_line[0]),
                time=time_used,
                memory=memory_used,
                error=error,
            )
        else:
            result_code, exit_code = self._supervisor_result_to_code(result_code)
            return TimeToolResult(
                status=Status.from_str(result_code),
                time=time_used,
                memory=memory_used,
                error=error,
            )
