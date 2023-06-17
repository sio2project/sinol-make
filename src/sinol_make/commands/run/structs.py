from typing import List
from dataclasses import dataclass

@dataclass
class ResultChange:
	solution: str
	group: int
	old_result: str
	result: str

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
