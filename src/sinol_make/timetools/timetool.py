import os
import sys
import signal
from threading import Timer

import subprocess
from typing import List

from sinol_make.structs.status_structs import Status
from sinol_make.structs.timetool_structs import TimeToolResult
from sinol_make.timetools import utils


class TimeTool:
    def __init__(self):
        pass

    def get_name(self) -> str:
        """
        :return: Name of this timetool.
        """
        raise NotImplementedError()

    def is_available(self) -> bool:
        """
        :return: True if this timetool is available.
        """
        raise NotImplementedError()

    def get_priority(self) -> int:
        """
        :return: Priority of this timetool.
        """
        raise NotImplementedError()

    def get_path(self) -> str:
        """
        :return: Path to the timetool.
        """
        raise NotImplementedError()

    def can_install(self) -> bool:
        """
        :return: True if this timetool can be automatically installed.
        """
        raise NotImplementedError()

    def is_latest_version(self) -> bool:
        """
        Check if this timetool is the latest version.
        :return: True if this timetool is the latest version.
        """
        raise NotImplementedError()

    def install(self):
        """
        Install the timetool.
        """
        raise NotImplementedError()

    def _get_env(self, time_limit, memory_limit):
        """
        Prepare environment for running the timetool.
        """
        return os.environ.copy()

    def _get_arguments(self, args: List[str], time_limit, memory_limit, result_file_path: str) -> List[str]:
        """
        Get arguments for running the timetool.
        :param args: Arguments to run the program with.
        :param time_limit: Time limit.
        :param memory_limit: Memory limit.
        :param result_file_path: Path to file where the time tool's results are saved.
        :return: List of arguments.
        """
        raise NotImplementedError()

    def _parse_result_file(self, result_file_path: str) -> TimeToolResult:
        """
        Parse the result file.
        :param result_file_path: Path to result file.
        :return: Result of the timetool run.
        """
        raise NotImplementedError()

    def run(self, arguments: List[str], result_file_path: str, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, time_limit=None, memory_limit=None, cwd=None) -> TimeToolResult:
        """
        Run the executable with the timetool.
        :param arguments: Arguments to run the program with.
        :param result_file_path: Path to file where the time tool's results are saved.
        :param stdin: Stdin.
        :param stdout: Stdout.
        :param stderr: Stderr.
        :param time_limit: Time limit.
        :param memory_limit: Memory limit.
        :param cwd: Current working directory. If None, the current working directory is used.
        :return: Result of the timetool run.
        """
        if cwd is None:
            cwd = os.getcwd()
        hard_time_limit = 2 * time_limit / 1000. if time_limit is not None else None
        env = self._get_env(time_limit, memory_limit)
        args = self._get_arguments(arguments, time_limit, memory_limit, result_file_path)
        args = utils.shellquote(args)
        p = subprocess.Popen(
            args,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
            shell=True,
            universal_newlines=True,
            env=env,
            cwd=cwd,
            preexec_fn=os.setpgrp
        )

        hard_limit_killed = False
        def oot_killer():
            nonlocal hard_limit_killed
            hard_limit_killed = True
            os.killpg(p.pid, signal.SIGKILL)
        kill_timer = Timer(hard_time_limit, oot_killer)
        kill_timer.start()

        return_code = p.wait()
        if kill_timer:
            kill_timer.cancel()

        result = self._parse_result_file(result_file_path)
        if hard_limit_killed:
            result.Status = Status.TL
        elif time_limit is not None and result.time > time_limit:
            result.Status = Status.TL
        elif memory_limit is not None and result.memory > memory_limit:
            result.Status = Status.ML
        return result
