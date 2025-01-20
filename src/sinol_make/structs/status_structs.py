from dataclasses import dataclass
from enum import Enum
from typing import List


class Status(str, Enum):
    PENDING = "  "
    CE = "CE"
    TL = "TL"
    ML = "ML"
    RE = "RE"
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
    # Whether the program should fail due to the error
    Fail: bool
    # Exit signal of the process
    ExitSignal: int
    # Comment received from checker.
    Comment: str
    # Stderr of the program (used for checkers/interactors)
    Stderr: List[str]
    # Original command line that was run
    Cmdline: str

    def __init__(self, status=None, Time=None, Memory=None, Points=0, Error=None, Fail=False, ExitSignal=0, Comment="",
                 Stderr=None, Cmdline=None):
        self.Status = status
        self.Time = Time
        self.Memory = Memory
        self.Points = Points
        self.Error = Error
        self.Fail = Fail
        self.ExitSignal = ExitSignal
        self.Comment = Comment
        self.Stderr = Stderr if Stderr is not None else []
        self.Cmdline = Cmdline

    @staticmethod
    def from_dict(dict):
        return ExecutionResult(
            status=Status.from_str(dict.get("Status", "")),
            Time=dict.get("Time", None),
            Memory=dict.get("Memory", None),
            Points=dict.get("Points", 0),
            Error=dict.get("Error", None),
            Fail=dict.get("Fail", False),
            ExitSignal=dict.get("ExitSignal", 0),
            Comment=dict.get("Comment", ""),
            Stderr=dict.get("Stderr", []),
            Cmdline=dict.get("Cmdline", ""),
        )

    def to_dict(self):
        return {
            "Status": str(self.Status),
            "Time": self.Time,
            "Memory": self.Memory,
            "Points": self.Points,
            "Error": self.Error,
            "Fail": self.Fail,
            "ExitSignal": self.ExitSignal,
            "Comment": self.Comment,
            "Stderr": self.Stderr,
            "Cmdline": self.Cmdline,
        }
