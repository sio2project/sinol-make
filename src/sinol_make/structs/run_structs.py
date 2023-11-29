from dataclasses import dataclass


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
