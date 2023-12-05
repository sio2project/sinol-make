import os
import subprocess
from typing import List, Union, Tuple

from sinol_make.structs.timetool_structs import TimeToolResult
from sinol_make.timetools.TimeToolManager import TimeToolManager


class Executor:
    def __init__(self, timetool_manager: TimeToolManager):
        self.timetool_manager = timetool_manager

    def run(self, arguments: List[str], stdin = None, stdout = None, stderr = None,
            cwd = None, return_out = False, shell = False) -> Union[int, Tuple[int, bytes, bytes]]:
        """
        Run the program.
        :param arguments: Arguments to run the program with.
        :param stdin: stdin of the program.
        :param stdout: stdout of the program.
        :param stderr: stderr of the program.
        :param cwd: Current working directory. If None, the current working directory is used.
        :param return_out: If True, returns stdout and stderr of the program (if they were `subprocess.PIPE`).
        :param shell: If True, runs the program in a shell.
        :return: Return code of the program.
        """
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(arguments, stdin=stdin, stdout=stdout, stderr=stderr, cwd=cwd, shell=shell)
        if return_out:
            out, err = process.communicate()
            return process.returncode, out, err
        else:
            process.communicate()
            return process.returncode

    def run_timetool(self, args: List[str], result_file_path: str, stdin = None, stdout = None,
                     stderr = None, time_limit = None, memory_limit = None, cwd = None) -> TimeToolResult:
        """
        Run the executable with the timetool.
        :param args: Arguments to run the program with.
        :param result_file_path: Path to file where the time tool's results are saved.
        :param stdin: Stdin.
        :param stdout: Stdout.
        :param stderr: Stderr.
        :param time_limit: Time limit.
        :param memory_limit: Memory limit.
        :param cwd: Current working directory. If None, the current working directory is used.
        :return: Result of the timetool run.
        """
        return self.timetool_manager.run(args, result_file_path, stdin, stdout, stderr,
                                         time_limit, memory_limit, cwd)
