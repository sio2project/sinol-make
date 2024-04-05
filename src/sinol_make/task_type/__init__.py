import os

from sinol_make.helpers import package_util
from sinol_make.task_type.base import BaseTaskType
from sinol_make.task_type.interactive_io import InteractiveIOTask
from sinol_make.task_type.normal import NormalTask


def get_task_type() -> BaseTaskType:
    if 'encdec' in os.listdir(os.getcwd()):
        # Encdec is not actually supported by sinol-make, as it isn't yet merged in OIOIOI.
        # (And probably never will)
        raise NotImplementedError("Encdec is not supported by sinol-make.")
    task_id = package_util.get_task_id()
    if package_util.any_files_matching_pattern(task_id, f"{task_id}soc.*"):
        return InteractiveIOTask(task_id)
    return NormalTask(task_id)
