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
	Time: int
	# Memory in KB
	Memory: float
