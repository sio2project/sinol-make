import subprocess
from typing import List, Tuple, Union

from sinol_make.structs.status_structs import ExecutionResult, Status


class BaseExecutor:
    """
    Base class for executors. Executors are used to run commands and measure their time and memory usage.
    """

    def __init__(self):
        pass

    def _wrap_command(self, command: List[str], result_file_path: str, time_limit: int, memory_limit: int) -> List[str]:
        """
        Wraps the command with the necessary tools to measure time and memory usage.
        """
        raise NotImplementedError()

    def _execute(self, command: List[str], time_limit: int, hard_time_limit: int, memory_limit: int,
                 result_file_path: str, executable: str, execution_dir: str, stdin: int, stdout: int,
                 stderr: Union[None, int], fds_to_close: Union[None, List[int]],
                 *args, **kwargs) -> Tuple[bool, bool, int, List[str]]:
        """
        This function should run subprocess.Popen with the given command and return a tuple of three values:
        - bool: whether the process was terminated due to time limit
        - bool: whether the process was terminated due to memory limit
        - int: return code of the process
        - List[str]: stderr of the process
        """
        raise NotImplementedError()

    def _parse_result(self, tle, mle, return_code, result_file_path) -> ExecutionResult:
        """
        Parses the result file and returns the result.
        """
        raise NotImplementedError()

    def execute(self, command: List[str], time_limit, hard_time_limit, memory_limit, result_file_path, executable,
                execution_dir, stdin=None, stdout=subprocess.DEVNULL, stderr=None,
                fds_to_close: Union[None, List[int]] = None, *args, **kwargs) -> ExecutionResult:
        """
        Executes the command and returns the result, stdout and stderr.
        """

        command = self._wrap_command(command, result_file_path, time_limit, memory_limit)
        cmdline = " ".join(command)
        tle, mle, return_code, proc_stderr = self._execute(cmdline, time_limit, hard_time_limit, memory_limit,
                                                           result_file_path, executable, execution_dir, stdin, stdout,
                                                           stderr, fds_to_close, *args, **kwargs)
        result = self._parse_result(tle, mle, return_code, result_file_path)
        result.Cmdline = cmdline
        if not result.Stderr:
            result.Stderr = proc_stderr
        if tle:
            result.Status = Status.TL
            result.Time = time_limit + 1
        elif mle:
            result.Status = Status.ML
            result.Memory = memory_limit + 1  # Add one so that the memory is red in the table
        elif return_code != 0:
            result.Status = Status.RE
            result.Error = f"Solution returned with code {return_code}"
        elif result.Status is None:
            result.Status = Status.OK
        return result
