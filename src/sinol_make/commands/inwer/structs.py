import os
from dataclasses import dataclass


@dataclass
class TestResult:
    test_path: str
    test_name: str
    test_group: str
    verified: bool
    valid: bool
    output: str

    def __init__(self, test_path):
        self.test_path = test_path
        self.test_name = os.path.split(test_path)[-1]
        group_number = "".join(filter(str.isdigit, self.test_name))
        if self.test_name.split('.')[0].split(group_number)[1] == 'ocen':
            self.test_group = group_number + 'ocen'
        else:
            self.test_group = group_number

        self.verified = False
        self.valid = False
        self.output = ""

    def update_result(self, valid, output):
        self.verified = True
        self.valid = valid
        self.output = output

@dataclass
class InwerExecution:
    test_path: str
    test_name: str
    inwer_exe_path: str

@dataclass
class VerificationResult:
    test_path: str
    valid: bool
    output: str
