from dataclasses import dataclass

from sinol_make.programs.solution import Solution
from sinol_make.tests.input import InputTest


@dataclass
class ExecutionData:
    """
    Represents data for execution of a solution on a specified test.
    """
    # Name of the solution
    name: str
    # Filename of the executable
    executable: str
    # Filename of the test
    test: str
    # Time limit for this test in milliseconds
    time_limit: int
    # Memory limit in KB
    memory_limit: int
    # Path to the timetool executable
    timetool_path: str


@dataclass
class PrintData:
    """
    Represents data for printing results of execution.
    """
    i: int


@dataclass
class RunExecution:
    solution: Solution
    test: InputTest
    time_limit: float
    memory_limit: float
