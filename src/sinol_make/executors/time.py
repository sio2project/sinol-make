import os
import signal
import subprocess
import sys
import time
from typing import List, Tuple, Union

import psutil
from sinol_make import util
from sinol_make.executors import BaseExecutor
from sinol_make.structs.status_structs import ExecutionResult, Status


class TimeExecutor(BaseExecutor):
    def _wrap_command(self, command: List[str], result_file_path: str, time_limit: int, memory_limit: int) -> List[str]:
        if sys.platform == 'darwin':
            time_name = 'gtime'
        elif sys.platform == 'linux':
            time_name = '\\time'
        else:
            util.exit_with_error("Measuring time with GNU time on Windows is not supported.")

        return [f'{time_name}', '-f', '"%U\\n%M\\n%x"', '-o', result_file_path] + command

    def _execute(self, cmdline: str, time_limit: int, hard_time_limit: int, memory_limit: int,
                 result_file_path: str, executable: str, execution_dir: str, stdin: int, stdout: int,
                 stderr: Union[None, int], fds_to_close: Union[None, List[int]],
                 *args, **kwargs) -> Tuple[bool, bool, int, List[str]]:
        timeout = False
        mem_limit_exceeded = False
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
                if executable_process is not None and executable_process.memory_info().rss > memory_limit * 1024:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    mem_limit_exceeded = True
                    break
            except psutil.NoSuchProcess:
                pass

            if time.time() - start_time > hard_time_limit:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                timeout = True
                break

        if stderr == subprocess.PIPE:
            _, proc_stderr = process.communicate()
            proc_stderr = proc_stderr.decode('utf-8').split('\n')
        else:
            proc_stderr = []
        return timeout, mem_limit_exceeded, 0, proc_stderr

    def _parse_result(self, tle, mle, return_code, result_file_path) -> ExecutionResult:
        program_exit_code = None
        result = ExecutionResult()
        if not tle:
            result.Time = 0
            result.Memory = 0
            with open(result_file_path, "r") as result_file:
                lines = result_file.readlines()
            if len(lines) == 4 and lines[0].startswith("Command exited with non-zero status"):
                result.Status = Status.RE
                exit_signal = int(lines[0].strip()[len("Command exited with non-zero status "):])
                program_exit_code = os.WTERMSIG(exit_signal)
            elif len(lines) == 3:
                """
                If programs runs successfully, the output looks like this:
                 - first line is CPU time in seconds
                 - second line is memory in KB
                 - third line is exit code
                This format is defined by -f flag in time command.
                """
                result.Time = round(float(lines[0].strip()) * 1000)
                result.Memory = int(lines[1].strip())
                program_exit_code = int(lines[2].strip())
            elif len(lines) > 0 and "Command terminated by signal " in lines[0]:
                """
                If there was a runtime error, the first line is the error message with signal number.
                For example:
                    Command terminated by signal 11
                """
                program_exit_code = int(lines[0].strip().split(" ")[-1])
            elif not mle:
                result.Status = Status.RE
                result.Error = "Unexpected output from time command:\n" + "".join(lines)
                result.Fail = True

        if program_exit_code is not None and program_exit_code != 0:
            program_exit_code = abs(program_exit_code)
            result.Status = Status.RE
            result.Error = f"Solution exited with code {program_exit_code}"
            result.ExitSignal = os.WTERMSIG(program_exit_code)
        return result
