from typing import List
import argparse
import subprocess

from sinol_make.structs.timetool_structs import TimeToolResult
from sinol_make.timetools.sio2jail_cpu import Sio2jailCpuTimeTool
from sinol_make.timetools.sio2jail_real import Sio2jailRealTimeTool
from sinol_make.timetools.timetool import TimeTool


class TimeToolManager:
    def __init__(self):
        self.possible_timetools: List[TimeTool] = [Sio2jailCpuTimeTool(), Sio2jailRealTimeTool()]
        self.used_timetool: TimeTool = None

    def get_possible_timetools(self) -> List[TimeTool]:
        """
        :return: List of possible timetools.
        """
        return self.possible_timetools

    def get_available_timetools(self) -> List[TimeTool]:
        """
        :return: List of available timetools.
        """
        res = []
        for timetool in self.get_possible_timetools():
            if timetool.can_install():
                res.append(timetool)
        return res

    def get_default_timetool(self) -> TimeTool:
        """
        :return: Default timetool.
        """
        res = None
        priority = 0
        for timetool in self.get_available_timetools():
            if timetool.get_priority() > priority:
                res = timetool
                priority = timetool.get_priority()
        return res

    def update_all_timetools(self):
        """
        Update/install all timetools.
        """
        for timetool in self.get_possible_timetools():
            if timetool.can_install() and not timetool.is_latest_version():
                print(f"Installing {timetool.get_install_name()}...")
                timetool.install()

    def add_arg(self, parser: argparse.ArgumentParser):
        """
        Add arguments to the parser.
        """
        default = self.get_default_timetool()
        parser.add_argument('-T', '--time-tool', dest='time_tool',
                            choices=[timetool.get_name() for timetool in self.get_available_timetools()],
                            help=f"tool to measure time and memory usage (default: {default.get_name()})",
                            default=default.get_name())

    def set_timetool(self, args):
        for timetool in self.get_available_timetools():
            if args.time_tool == timetool.get_name():
                self.used_timetool = timetool
                return
        raise ValueError(f"Unknown timetool: {args.time_tool}")

    def run(self, args: List[str], result_file_path: str, stdin=None, stdout=None,
            stderr=None, time_limit=None, memory_limit=None, cwd=None) -> TimeToolResult:
        """
        Run the executable with the timetool.
        :param args: Arguments to run the program with.
        :param result_file_path: Path to file to write time tool's result.
        :param stdin: Stdin.
        :param stdout: Stdout.
        :param stderr: Stderr.
        :param time_limit: Time limit.
        :param memory_limit: Memory limit.
        :param cwd: Current working directory. If None, the current working directory is used.
        :return: Result of the timetool run.
        """
        return self.used_timetool.run(args, result_file_path, stdin, stdout, stderr,
                                      time_limit, memory_limit, cwd)
