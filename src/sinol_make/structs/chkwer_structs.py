import os
from dataclasses import dataclass
from typing import Dict

from sio3pack.test import Test


@dataclass
class TestResult:
    test: Test
    run: bool
    points: int
    ok: bool
    comment: str

    def __init__(self, test: Test):
        self.test = test

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
    test: Test
    checker_exe: str
    model_exe: str


@dataclass
class RunResult:
    test: Test
    ok: bool
    points: int
    comment: str
