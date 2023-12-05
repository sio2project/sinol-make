from dataclasses import dataclass
from typing import Union

from sinol_make.structs.status_structs import Status


@dataclass
class TimeToolResult:
    status: Status
    time: float
    memory: float
    error: Union[str, None]

    def __init__(self, status: Status, time: float, memory: float, error: Union[str, None] = None):
        self.status = status
        self.time = time
        self.memory = memory
        self.error = error
