from dataclasses import dataclass

from sio3pack import LocalFile
from sio3pack.test.test import Test

@dataclass
class ExecutionData:
    """
    Represents data for execution of a solution on a specified test.
    """
    # The solution
    solution: LocalFile
    # Filename of the executable
    executable: str
    # Filename of the test
    test: Test
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
