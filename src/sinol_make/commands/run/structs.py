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
