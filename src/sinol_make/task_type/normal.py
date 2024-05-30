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
            return [("checker", [self.checker], {"remove_all_cache": True})]
        else:
            self._has_checker = False
            self._check_had_checker(False)
        return []


    def _run_checker(self, input_file, output_file_path, answer_file_path) -> List[str]:
        command = [self.checker_exe, input_file, output_file_path, answer_file_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        process.wait()
        return process.communicate()[0].decode("utf-8").splitlines()

    def _run_program_oiejq(self, timetool_path, env, executable, result_file_path, input_file_path, output_file_path,
                           answer_file_path, time_limit, memory_limit, hard_time_limit, execution_dir):

        command = self._wrap_with_oiejq(f'"{executable}"', timetool_path)
        env = self._prepare_oiejq_env(env, memory_limit)
        with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file, \
                open(result_file_path, "w") as result_file:
            timeout, mem_limit_exceeded = self._run_subprocess(True, True, executable, memory_limit, hard_time_limit,
                                                               command, shell=True, stdin=input_file,
                                                               stdout=output_file, stderr=result_file, env=env,
                                                               preexec_fn=os.setsid, cwd=execution_dir)
        return timeout, mem_limit_exceeded

    def _run_program_time(self, timetool_path, env, executable, result_file_path, input_file_path, output_file_path,
                          answer_file_path, time_limit, memory_limit, hard_time_limit, execution_dir):

        command = self._wrap_with_time([f'"{executable}"'], result_file_path)
        with open(input_file_path, "r") as input_file, open(output_file_path, "w") as output_file:
            timeout, mem_limit_exceeded = self._run_subprocess(False, True, executable, memory_limit, hard_time_limit,
                                                               ' '.join(command), shell=True, stdin=input_file,
                                                               stdout=output_file,
                                                               stderr=subprocess.DEVNULL, preexec_fn=os.setsid,
                                                               cwd=execution_dir)
        return timeout, mem_limit_exceeded
