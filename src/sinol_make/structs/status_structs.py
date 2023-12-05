from dataclasses import dataclass
from enum import Enum
from typing import List


class Status(str, Enum):
    PENDING = "  "
    CE = "CE"
    TL = "TL"
    ML = "ML"
    RE = "RE"
    RV = "RV"
    WA = "WA"
    OK = "OK"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @staticmethod
    def from_str(status):
        if status == "CE":
            return Status.CE
        elif status == "TL" or status == "TLE":
            return Status.TL
        elif status == "ML" or status == "MLE":
            return Status.ML
        elif status == "RE":
            return Status.RE
        elif status == "WA":
            return Status.WA
        elif status == "RV":
            return Status.RV
        elif status == "OK":
            return Status.OK
        elif status == "  ":
            return Status.PENDING
        else:
            raise ValueError(f"Unknown status: '{status}'")

    @staticmethod
    def possible_statuses():
        return [Status.PENDING, Status.CE, Status.TL, Status.ML, Status.RE, Status.WA, Status.OK]


@dataclass
class ResultChange:
    solution: str
    group: int
    old_result: Status
    result: Status


@dataclass
class TotalPointsChange:
    solution: str
    old_points: int
    new_points: int


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
    unknown_change: bool


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
    # Whether to exit with error if ``Error`` is set
    ExitOnError: bool = True

    def __init__(self, status=None, Time=None, Memory=None, Points=0, Error=None, ExitOnError=True):
        self.Status = status
        self.Time = Time
        self.Memory = Memory
        self.Points = Points
        self.Error = Error
        self.ExitOnError = ExitOnError


    @staticmethod
    def from_dict(dict):
        return ExecutionResult(
            status=Status.from_str(dict.get("Status", "")),
            Time=dict.get("Time", None),
            Memory=dict.get("Memory", None),
            Points=dict.get("Points", 0),
            Error=dict.get("Error", None),
            ExitOnError=dict.get("ExitOnError", True)
        )

    def to_dict(self):
        return {
            "Status": str(self.Status),
            "Time": self.Time,
            "Memory": self.Memory,
            "Points": self.Points,
            "Error": self.Error,
            "ExitOnError": self.ExitOnError
        }
