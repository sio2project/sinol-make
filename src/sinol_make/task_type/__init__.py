import os
import subprocess
from fractions import Fraction
from typing import Tuple, List, Type

from sinol_make import util
from sinol_make.executors.sio2jail import Sio2jailExecutor
from sinol_make.executors.time import TimeExecutor
from sinol_make.helpers import package_util, paths, cache, oicompare
from sinol_make.helpers.classinit import RegisteredSubclassesBase
from sinol_make.interfaces.Errors import CheckerException
from sinol_make.structs.status_structs import ExecutionResult


class BaseTaskType(RegisteredSubclassesBase):
    abstract = True

    @classmethod
    def identify(cls) -> Tuple[bool, int]:
        """
        Returns a tuple of two values:
        - bool: whether the task is of this type
        - int: priority of this task type
        """
        raise NotImplementedError()

    @classmethod
    def get_task_type(cls) -> Type["BaseTaskType"]:
        task_type = None
        max_priority = -1
        for subclass in cls.subclasses:
            is_task, priority = subclass.identify()
            if is_task and priority > max_priority:
                task_type = subclass
                max_priority = priority
        return task_type

    @staticmethod
    def name() -> str:
        """
        Returns the name of task type.
        """
        raise NotImplementedError()

    def _check_task_type_changed(self):
        """
        Checks if task type has changed and if so, deletes cache.
        """
        name = self.name()
        if os.path.exists(paths.get_cache_path("task_type")):
            with open(paths.get_cache_path("task_type"), "r") as f:
                if f.read().strip() != name:
                    cache.remove_results_cache()
        with open(paths.get_cache_path("task_type"), "w") as f:
            f.write(name)

    def __init__(self, timetool, sio2jail_path):
        super().__init__()
        self.timetool = timetool
        self.sio2jail_path = sio2jail_path
        self.has_checker = False
        self.checker_path = None

        if self.timetool == 'time':
            self.executor = TimeExecutor()
        elif self.timetool == 'sio2jail':
            self.executor = Sio2jailExecutor(sio2jail_path)
        else:
            util.exit_with_error(f"Unknown timetool {self.timetool}")
        self._check_task_type_changed()

    def _check_had_file(self, file, has_file):
        """
        Checks if there was a file (e.g. checker) and if it is now removed (or the other way around) and if so,
        removes tests cache.
        """
        had_file = os.path.exists(paths.get_cache_path(file))
        if (had_file and not has_file) or (not had_file and has_file):
            cache.remove_results_cache()
        if has_file:
            with open(paths.get_cache_path(file), "w") as f:
                f.write("")
        else:
            try:
                os.remove(paths.get_cache_path(file))
            except FileNotFoundError:
                pass

    def additional_files_to_compile(self) -> List[Tuple[str, str, str, bool, bool]]:
        """
        Returns a list of tuples of two values:
        - str: source file path to compile
        - str: path to the compiled file
        - str: name of the compiled file
        - bool: whether the program should fail on compilation error
        - bool: whether all cache should be cleared on file change
        """
        ret = []
        task_id = package_util.get_task_id()
        checker = package_util.get_files_matching_pattern(task_id, f'{task_id}chk.*')
        if len(checker) > 0:
            self.has_checker = True
            checker = checker[0]
            checker_basename = os.path.basename(checker)
            self.checker_path = paths.get_executables_path(checker_basename + ".e")
            ret += [(checker, self.checker_path, "checker", True, True)]
        self._check_had_file("checker", self.has_checker)
        return ret

    @staticmethod
    def run_outgen() -> bool:
        """
        Whether outgen should be run.
        """
        return True

    @staticmethod
    def allow_chkwer() -> bool:
        """
        Whether chkwer should be allowed to run.
        """
        return True

    def _output_to_fraction(self, output_str):
        if not output_str:
            return Fraction(100, 1)
        if isinstance(output_str, bytes):
            output_str = output_str.decode('utf-8')
        try:
            return Fraction(output_str)
        except ValueError:
            raise CheckerException(f'Invalid checker output, expected float, percent or fraction, got "{output_str}"')
        except ZeroDivisionError:
            raise CheckerException(f'Zero division in checker output "{output_str}"')
        except TypeError:
            raise CheckerException(f'Invalid checker output "{output_str}"')

    def _parse_checker_output(self, output: List[str]) -> Tuple[bool, Fraction, str]:
        while len(output) < 3:
            output.append('')

        if output[0].strip() == "OK":
            points = self._output_to_fraction(output[2])
            return True, points, output[1].strip()
        else:
            return False, Fraction(0, 1), output[1].strip()

    def _run_checker(self, input_file_path, output_file_path, answer_file_path) -> Tuple[bool, Fraction, str]:
        proc = subprocess.Popen([self.checker_path, input_file_path, output_file_path, answer_file_path],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        output, stderr = proc.communicate()
        if proc.returncode > 2:
            return False, Fraction(0, 1), (f"Checker returned with code {proc.returncode}, "
                                           f"stderr: '{stderr.decode('utf-8')}'")
        return self._parse_checker_output(output.decode('utf-8').split('\n'))

    def _run_diff(self, output_file_path, answer_file_path) -> Tuple[bool, Fraction, str]:
        same = oicompare.compare(output_file_path, answer_file_path)
        if same:
            return True, Fraction(100, 1), ""
        else:
            return False, Fraction(0, 1), ""

    def _run_oicompare(self, output_file_path, answer_file_path) -> Tuple[bool, Fraction, str]:
        path = oicompare.get_path()
        proc = subprocess.Popen([path, output_file_path, answer_file_path, 'english_abbreviated'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()
        output, stderr = proc.communicate()
        if proc.returncode == 0:
            return True, Fraction(100, 1), ""
        elif proc.returncode == 1:
            return False, Fraction(0, 1), output.decode('utf-8').strip()
        else:
            raise CheckerException(f"!!! oicompare failed with code {proc.returncode}. This is a huge bug, please report"
                                   f" it here https://github.com/sio2project/sinol-make/issues/new/choose and provide "
                                   f"these files: {output_file_path}, {answer_file_path}.\n"
                                   f"Output: {output.decode('utf-8').strip()}\n"
                                   f"Stderr: {stderr.decode('utf-8').strip()}")

    def check_output(self, input_file_path, output_file_path, answer_file_path) -> Tuple[bool, Fraction, str]:
        """
        Runs the checker (or runs diff) and returns a tuple of three values:
        - bool: whether the solution is correct
        - Fraction: percentage of the score
        - str: optional comment
        """
        if self.has_checker:
            return self._run_checker(input_file_path, output_file_path, answer_file_path)
        elif oicompare.check_installed():
            return self._run_oicompare(output_file_path, answer_file_path)
        else:
            return self._run_diff(output_file_path, answer_file_path)

    def run(self, time_limit, hard_time_limit, memory_limit, input_file_path, output_file_path, answer_file_path,
            result_file_path, executable, execution_dir) -> ExecutionResult:
        raise NotImplementedError
