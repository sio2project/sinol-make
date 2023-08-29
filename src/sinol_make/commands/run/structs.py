from typing import List
from dataclasses import dataclass

from sinol_make.structs.status_structs import Status


@dataclass
class ResultChange:
    solution: str
    group: int
    old_result: Status
    result: Status

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
    # Result status of execution. Possible values
    #  can be found in `Status` enum definition.
    Status: Status
    # Time in milliseconds
    Time: float
    # Memory in KB
    Memory: int
    # Points for this test
    Points: int
    # Error message
    Error: str

    def __init__(self, status=None, Time=None, Memory=None, Points=0, Error=None):
        self.Status = status
        self.Time = Time
        self.Memory = Memory
        self.Points = Points
        self.Error = Error

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
