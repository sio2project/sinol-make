import os
from dataclasses import dataclass
from typing import Dict

from sinol_make.helpers import package_util


@dataclass
class TestResult:
    test_path: str
    test_name: str
    test_group: str
    run: bool
    points: int
    ok: bool
    comment: str

    def __init__(self, test_path, task_id):
        self.test_path = test_path
        self.test_name = os.path.split(test_path)[-1]
        self.test_group = str(package_util.get_group(self.test_path, task_id))

        self.comment = ""
        self.points = 0
        self.ok = False
        self.run = False

    def set_results(self, points, ok, output):
        self.run = True
        self.points = points
        self.ok = ok
        self.comment = output


@dataclass
class TableData:
    """
    Data used for printing table with verification results.
    """

    # Dictionary with test path as key and verification result as value.
    results: Dict[str, TestResult]

    # Number of executions finished
    i: int

    # Task id
    task_id: str

    # Max score per test for this contest type
    max_score: int


@dataclass
class ChkwerExecution:
    in_test_path: str
    in_test_name: str
    out_test_path: str
    checker_exe: str
    model_exe: str


@dataclass
class RunResult:
    test_path: str
    ok: bool
    points: int
    comment: str
