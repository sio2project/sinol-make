import os
import subprocess
from typing import List

from sinol_make.helpers import package_util, paths, cache
from sinol_make.task_type.base import BaseTaskType


class NormalTask(BaseTaskType):
    def __init__(self, task_id):
        super().__init__(task_id)
        self.checker = None
        self.checker_exe = None

    def _check_had_checker(self, has_checker):
        """
        Checks if there was a checker and if it is now removed (or the other way around) and if so, removes tests cache.
        In theory, removing cache after adding a checker is redundant, because during its compilation, the cache is
        removed.
        """
        had_checker = os.path.exists(paths.get_cache_path("checker"))
        if (had_checker and not has_checker) or (not had_checker and has_checker):
            cache.remove_results_cache()
        if has_checker:
            with open(paths.get_cache_path("checker"), "w") as f:
                f.write("")
        else:
            try:
                os.remove(paths.get_cache_path("checker"))
            except FileNotFoundError:
                pass

    def get_files_to_compile(self):
        super().get_files_to_compile()
        checkers = package_util.get_files_matching_pattern(self.task_id, f'{self.task_id}chk.*')
        if checkers:
            self._has_checker = True
            self.checker = checkers[0]
            self._check_had_checker(True)
            self.checker_exe = paths.get_executables_path(package_util.get_executable(self.checker))
            return [("checker", [self.checker], {"is_checker": True})]
        else:
            self._has_checker = False
            self._check_had_checker(False)
        return []

    def _run_checker(self, input_file, output_file_path, answer_file_path) -> List[str]:
        command = [self.checker_exe, input_file, output_file_path, answer_file_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        process.wait()
        return process.communicate()[0].decode("utf-8").splitlines()
