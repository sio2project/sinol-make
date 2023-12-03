from typing import Union, List
import os
import yaml

from sinol_make import util
from sinol_make.compilers.CompilersManager import CompilerManager
from sinol_make.executor import Executor
from sinol_make.helpers import package_util
from sinol_make.programs.checker import Checker
from sinol_make.programs.ingen import Ingen
from sinol_make.programs.inwer import Inwer
from sinol_make.programs.solution import Solution
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest
from sinol_make.timetools.TimeToolManager import TimeToolManager


class BaseCommand:
    """
    Base class for command
    """

    def __init__(self, timetool_manager: TimeToolManager, executor: Executor):
        self.config = None
        self.task_id = None
        self.compiler_manager: CompilerManager = None
        self.timetool_manager = timetool_manager
        self.executor = executor
        self.args = None

    @staticmethod
    def require_package():
        """
        Require package for command
        """
        return True

    def ingen_exists(self) -> bool:
        """
        Check if ingen exists.
        """
        try:
            self.get_ingen()
            return True
        except FileNotFoundError:
            return False

    def checker_exists(self) -> bool:
        """
        Check if checker exists.
        """
        try:
            self.get_checker()
            return True
        except FileNotFoundError:
            return False

    def get_ingen(self, file_path: Union[str, None] = None) -> Ingen:
        """
        Get ingen. If file_path is not None, then the first ingen found is returned
        :param file_path: If specified, this file will be used.
        :return: Ingen.
        """
        return Ingen(self.executor, self.compiler_manager, self.task_id, file_path)

    def get_inwer(self, file_path: Union[str, None] = None) -> Inwer:
        """
        Get inwer. If file_path is not None, then the first inwer found is returned
        :param file_path: If specified, this file will be used.
        :return: Inwer.
        """
        return Inwer(self.executor, self.compiler_manager, self.task_id, file_path)

    def get_checker(self, file_path: Union[str, None] = None) -> Checker:
        """
        Get checker. If file_path is not None, then the first checker found is returned
        :param file_path: If specified, this file will be used.
        :return: Checker.
        """
        return Checker(self.executor, self.compiler_manager, self.task_id, file_path)

    def get_solution(self, file_path: Union[str, None] = None) -> Solution:
        """
        Get solution.
        :param file_path: File path to the solution.
        :return: Solution.
        """
        return Solution(self.executor, self.compiler_manager, self.task_id, file_path)

    def get_all_solutions(self, args_solutions: Union[List[str], None] = None) -> List[Solution]:
        """
        Returns list of solutions to run.
        :param args_solutions: Solutions specified in command line arguments. If None, all solutions are returned.
        :return: List of solutions to run.
        """
        res = []
        if args_solutions is None:
            for file in os.listdir(os.path.join(os.getcwd(), 'prog')):
                try:
                    solution = self.get_solution(os.path.join(os.getcwd(), 'prog', file))
                except FileNotFoundError:
                    continue
                res.append(solution)
        else:
            for file in args_solutions:
                wrong = True
                try:
                    solution = self.get_solution(file)
                    wrong = False
                    res.append(solution)
                except FileNotFoundError:
                    pass
                if not os.path.isabs(file):
                    try:
                        solution = self.get_solution(os.path.join(os.getcwd(), 'prog', file))
                        wrong = False
                        res.append(solution)
                    except FileNotFoundError:
                        pass
                if wrong:
                    util.exit_with_error(f'File {file} does not exist or is not a solution.')
        return sorted(res, key=package_util.get_executable_key)

    def get_correct_solution(self) -> Solution:
        """
        Get correct solution.
        :return: Solution.
        """
        solution = self.get_solution()
        if not solution.is_correct_solution():
            util.exit_with_error(f'Correct solution for task {self.task_id} does not exist.')
        return solution

    def get_corresponding_test(self, test: Union[InputTest, OutputTest],
                               exists: bool = True) -> Union[InputTest, OutputTest]:
        """
        Get corresponding test for given test.
        :param test: Test
        :param exists: If True, then the test must exist.
        :return: Corresponding test
        """
        if isinstance(test, InputTest):
            return OutputTest(self.task_id, os.path.splitext(test.basename)[0] + '.out', exists=exists)
        elif isinstance(test, OutputTest):
            return InputTest(self.task_id, os.path.splitext(test.basename)[0] + '.in', exists=exists)
        else:
            raise ValueError('Invalid test type.')

    def get_name(self):
        """
        Get name of command
        """
        raise NotImplementedError()

    def configure_subparser(self, subparser):
        """
        Configure subparser for command
        """
        raise NotImplementedError()

    def run(self, args):
        """
        Run command
        """
        self.compiler_manager = CompilerManager(args)
        self.args = args

        if self.require_package():
            util.exit_if_not_package()
            self.task_id = package_util.get_task_id()
            with open(os.path.join(os.getcwd(), 'config.yml'), 'r') as config_file:
                self.config = yaml.load(config_file, Loader=yaml.FullLoader)

    def base_run(self, args):
        """
        Call run command in the base class. Used in tests. Do not use in other places.
        """
        super(type(self), self).run(args)
