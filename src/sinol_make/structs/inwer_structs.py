import os
from dataclasses import dataclass
from typing import Dict

from sio3pack.test import Test

from sinol_make.helpers import package_util


@dataclass
class TestResult:
    test: Test
    verified: bool
    valid: bool
    output: str

    def __init__(self, test: Test):
        self.test = test

        self.verified = False
        self.valid = False
        self.output = ""

    def set_results(self, valid, output):
        self.verified = True
        self.valid = valid
        self.output = output

@dataclass
class TableData:
    """
    Data used for printing table with verification results.
    """

    # Dictionary with test as key and verification result as value.
    results: Dict[Test, TestResult]

    # Number of executions finished
    i: int

@dataclass
class InwerExecution:
    test: Test
    inwer_exe_path: str

@dataclass
class VerificationResult:
    test: Test
    valid: bool
    output: str
