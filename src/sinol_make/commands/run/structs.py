from typing import List
from dataclasses import dataclass

@dataclass
class ResultChange:
    solution: str
    group: int
    old_result: str
    result: str

@dataclass
class PointsChange:
    solution: str
    group: int
    old_points: int
    new_points: int

@dataclass
class ValidationResult:
    added_solutions: set
    removed_solutions: set
    added_groups: set
    removed_groups: set
    changes: List[ResultChange]
    expected_scores: dict
    new_expected_scores: dict

@dataclass
class ExecutionResult:
    # Result status of execution. Can be one of:
    # "OK", "WA", "TL", "ML", "RE", "CE"
    Status: str
    # Time in milliseconds
    Time: float
    # Memory in KB
    Memory: int
    # Points for this test
    Points: int
    # Error message
    Error: str

    def __init__(self, status=None):
        self.Status = status
        self.Time = None
        self.Memory = None
        self.Points = 0
        self.Error = None

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
    # Dictionary of pids for each execution
    execution_pids: dict[dict[str, int]]


@dataclass
class PrintData:
    """
    Represents data for printing results of execution.
    """

    i: int
