import os
import signal
import subprocess
import sys
from typing import List, Tuple, Union

from sinol_make.executors import BaseExecutor
from sinol_make.structs.status_structs import ExecutionResult, Status


class OiejqExecutor(BaseExecutor):
    def __init__(self, oiejq_path):
        super().__init__()
        self.oiejq_path = oiejq_path

    def _wrap_command(self, command: List[str], result_file_path: str) -> List[str]:
        return [f'"{self.oiejq_path}"'] + command

    def _execute(self, command: List[str], time_limit: int, hard_time_limit: int, memory_limit: int,
                 result_file_path: str, executable: str, execution_dir: str, stdin: int, stdout: int,
                 stderr: Union[None, int], fds_to_close: Union[None, List[int]],
                 *args, **kwargs) -> Tuple[bool, bool, int, List[str]]:
        env = os.environ.copy()
        env["MEM_LIMIT"] = f'{memory_limit}K'
        env["MEASURE_MEM"] = "1"
        env["UNDER_OIEJQ"] = "1"

        timeout = False
        with open(result_file_path, "w") as result_file:
            process = subprocess.Popen(' '.join(command), *args, shell=True, stdin=stdin, stdout=stdout,
                                       stderr=result_file, env=env, preexec_fn=os.setpgrp, cwd=execution_dir, **kwargs)
            if fds_to_close is not None:
                for fd in fds_to_close:
                    os.close(fd)

            try:
                process.wait(timeout=hard_time_limit)
            except subprocess.TimeoutExpired:
                timeout = True
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                process.communicate()

        return timeout, False, 0, []

    def _parse_time(self, time_str):
        if len(time_str) < 3: return -1
        return int(time_str[:-2])

    def _parse_memory(self, memory_str):
        if len(memory_str) < 3: return -1
        return int(memory_str[:-2])

    def _parse_result(self, tle, mle, return_code, result_file_path) -> ExecutionResult:
        result = ExecutionResult()
        if not tle:
            with open(result_file_path, "r") as result_file:
                lines = result_file.readlines()

            stderr = []
            i = 0
            while lines[i].strip() != "-------------------------":
                stderr.append(lines[i])
                i += 1
            result.Stderr = stderr[:-1]  # oiejq adds a blank line.

            for line in lines:
                line = line.strip()
                if ": " in line:
                    (key, value) = line.split(": ")[:2]
                    if key == "Time":
                        result.Time = self._parse_time(value)
                    elif key == "Memory":
                        result.Memory = self._parse_memory(value)
                    else:
                        setattr(result, key, value)

            if lines[-2].strip() == 'Details':
                result.Error = lines[-1].strip()
                if lines[-1].startswith("process exited due to signal"):
                    result.ExitSignal = int(lines[-1].strip()[len("process exited due to signal "):])
            result.Status = Status.from_str(result.Status)
        return result
