import os
import signal
import subprocess
import time
import psutil
from typing import List, Tuple, Union

from sinol_make.executors import BaseExecutor
from sinol_make.structs.status_structs import ExecutionResult, Status


class DetailedExecutor(BaseExecutor):
    """
    Executor which doesn't use time or sio2jail for measuring time and memory usage.
    """

    def _wrap_command(self, command: List[str], result_file_path: str, time_limit: int, memory_limit: int) -> List[str]:
        return command

    def _execute(self, cmdline: str, time_limit: int, hard_time_limit: int, memory_limit: int,
                 result_file_path: str, executable: str, execution_dir: str, stdin: int, stdout: int,
                 stderr: Union[None, int], fds_to_close: Union[None, List[int]],
                 *args, **kwargs) -> Tuple[bool, bool, int, List[str]]:
        timeout = False
        mem_used = 0
        if stderr is None:
            stderr = subprocess.PIPE
        process = subprocess.Popen(cmdline, shell=True, *args, stdin=stdin, stdout=stdout, stderr=stderr,
                                   preexec_fn=os.setpgrp, cwd=execution_dir, **kwargs)
        if fds_to_close is not None:
            for fd in fds_to_close:
                os.close(fd)

        start_time = time.time()
        while process.poll() is None:
            try:
                time_process = psutil.Process(process.pid)
                executable_process = None
                for child in time_process.children():
                    if child.name() == executable:
                        executable_process = child
                        break
                if executable_process is not None:
                    mem_used = max(mem_used, executable_process.memory_info().rss)
                if executable_process is not None and mem_used > memory_limit * 1024:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    break
            except psutil.NoSuchProcess:
                pass

            if time.time() - start_time > hard_time_limit:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                break
        time_used = time.time() - start_time
        mem_used = mem_used // 1024

        with open(result_file_path, "w") as result_file:
            result_file.write(f"{time_used}\n{mem_used}\n{process.returncode}\n")

        if stderr == subprocess.PIPE:
            _, proc_stderr = process.communicate()
            proc_stderr = proc_stderr.decode('utf-8').split('\n')
        else:
            proc_stderr = []
        return timeout, mem_used > memory_limit, 0, proc_stderr

    def _parse_result(self, tle, mle, return_code, result_file_path) -> ExecutionResult:
        result = ExecutionResult()
        program_exit_code = 0
        with open(result_file_path, "r") as result_file:
            lines = result_file.readlines()
        if len(lines) == 3:
            result.Time = float(lines[0].strip())
            result.Memory = float(lines[1].strip())
            program_exit_code = int(lines[2].strip())
        else:
            result.Status = Status.RE
            result.Error = "Unexpected output from execution:\n" + "".join(lines)
            result.Fail = True
        if program_exit_code != 0:
            program_exit_code = abs(program_exit_code)
            result.Status = Status.RE
            result.Error = f"Program exited with code {program_exit_code}"
            result.ExitSignal = os.WTERMSIG(program_exit_code)
        return result
