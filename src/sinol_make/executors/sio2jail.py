import os
import signal
import subprocess
import sys
import traceback
from typing import List, Tuple, Union

from sinol_make import util
from sinol_make.executors import BaseExecutor
from sinol_make.structs.status_structs import ExecutionResult, Status


class Sio2jailExecutor(BaseExecutor):
    def __init__(self, sio2jail_path):
        super().__init__()
        self.sio2jail_path = sio2jail_path

    def _wrap_command(self, command: List[str], result_file_path: str, time_limit: int, memory_limit: int) -> List[str]:
        # see: https://github.com/sio2project/sioworkers/blob/738aa7a4e93216b0900ca128d6d48d40cd38bc1e/sio/workers/executors.py#L608
        return [f'"{self.sio2jail_path}"', '--mount-namespace', 'off', '--pid-namespace', 'off', '--uts-namespace',
                'off', '--ipc-namespace', 'off', '--net-namespace', 'off', '--capability-drop', 'off',
                '--user-namespace', 'off', '--instruction-count-limit', f'{int(2 * time_limit)}M',
                '--rtimelimit', f'{int(16 * time_limit + 1000)}ms', '--memory-limit', f'{int(memory_limit)}K',
                '--output-limit', '51200K', '--output', 'oiaug', '--stderr', '--'] + command

    def _execute(self, cmdline: str, time_limit: int, hard_time_limit: int, memory_limit: int,
                 result_file_path: str, executable: str, execution_dir: str, stdin: int, stdout: int,
                 stderr: Union[None, int], fds_to_close: Union[None, List[int]],
                 *args, **kwargs) -> Tuple[bool, bool, int, List[str]]:
        env = os.environ.copy()
        env['UNDER_SIO2JAIL'] = "1"
        with open(result_file_path, "w") as result_file:
            try:
                process = subprocess.Popen(cmdline, *args, shell=True, stdin=stdin, stdout=stdout, env=env,
                                           stderr=result_file, preexec_fn=os.setpgrp, cwd=execution_dir, **kwargs)
            except TypeError as e:
                print(util.error(f"Invalid command: `{cmdline}`"))
                raise e
            if fds_to_close is not None:
                for fd in fds_to_close:
                    os.close(fd)
            process.wait()

        return False, False, 0, []

    def _parse_time(self, time_str):
        if len(time_str) < 3: return -1
        return int(time_str[:-2])

    def _parse_memory(self, memory_str):
        if len(memory_str) < 3: return -1
        return int(memory_str[:-2])

    def _parse_result(self, _, mle, return_code, result_file_path) -> ExecutionResult:
        result = ExecutionResult()
        with open(result_file_path, "r") as result_file:
            lines = result_file.readlines()

        try:
            result.stderr = lines[:-2]
            status, code, time_ms, _, memory_kb, _ = lines[-2].strip().split()
            message = lines[-1].strip()
            result.Time = int(time_ms)
            result.Memory = int(memory_kb)
        except:
            output = "".join(lines)
            util.exit_with_error("Could not parse sio2jail output:"
                f"\n---\n{output}"
                f"\n---\n{traceback.format_exc()}")

        # ignoring `status` is weird, but sio2 does it this way
        if message == 'ok':
            result.Status = Status.OK
        elif message == 'time limit exceeded':
            result.Status = Status.TL
        elif message == 'real time limit exceeded':
            result.Status = Status.TL
            result.Error = message
        elif message == 'memory limit exceeded':
            result.Status = Status.ML
            # TODO: sinol-make does not support "OLE"
            result.Status = Status.RE
            result.Error = message
        elif message.startswith('intercepted forbidden syscall'):
            # TODO: sinol-make does not support "RV"
            result.Status = Status.RE
            result.Error = message
        elif message.startswith('process exited due to signal'):
            code = message[len('process exited due to signal '):]
            result.Status = Status.RE
            result.Error = message
            result.ExitSignal = int(code)
        else:
            result.Status = Status.RE
            result.Error = 'Unrecognized Sio2jail result: ' + message

        return result
