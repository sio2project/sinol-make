import os
from dataclasses import dataclass
from typing import Dict

import yaml

from sinol_make.helpers import paths

from sinol_make.structs.status_structs import ExecutionResult


@dataclass
class CacheTest:
    # Time limit when this solution was cached
    time_limit: int
    # Memory limit when this solution was cached
    memory_limit: int
    # Time tool used when this solution was cached
    time_tool: str
    # Cached result
    result: ExecutionResult

    def __init__(self, time_limit=0, memory_limit=0, time_tool="", result=None):
        if result is None:
            result = ExecutionResult()
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.time_tool = time_tool
        self.result = result

    def to_dict(self) -> Dict:
        return {
            "time_limit": self.time_limit,
            "memory_limit": self.memory_limit,
            "time_tool": self.time_tool,
            "result": self.result.to_dict()
        }


@dataclass
class CacheFile:
    # md5sum of solution
    md5sum: str
    # Path to the executable
    executable_path: str
    # Test results
    tests: Dict[str, CacheTest]

    def __init__(self, md5sum="", executable_path="", tests=None):
        if tests is None:
            tests = {}
        self.md5sum = md5sum
        self.executable_path = executable_path
        self.tests = tests

    def to_dict(self) -> Dict:
        return {
            "md5sum": self.md5sum,
            "executable_path": self.executable_path,
            "tests": {k: v.to_dict() for k, v in self.tests.items()}
        }

    @staticmethod
    def from_dict(dict) -> 'CacheFile':
        return CacheFile(
            md5sum=dict.get("md5sum", ""),
            executable_path=dict.get("executable_path", ""),
            tests={k: CacheTest(
                time_limit=v["time_limit"],
                memory_limit=v["memory_limit"],
                time_tool=v["time_tool"],
                result=ExecutionResult.from_dict(v["result"])
            ) for k, v in dict.get("tests", {}).items()}
        )

    def save(self, solution_path: str):
        os.makedirs(paths.get_cache_path("md5sums"), exist_ok=True)
        with open(paths.get_cache_path("md5sums", os.path.basename(solution_path)), 'w') as cache_file:
            yaml.dump(self.to_dict(), cache_file)
