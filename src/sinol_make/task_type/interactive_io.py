import os
import signal
from threading import Thread
from typing import Tuple, Union

from sinol_make.helpers import package_util, paths
from sinol_make.structs.status_structs import ExecutionResult, Status
from sinol_make.task_type import BaseTaskType


class InteractiveIOTask(BaseTaskType):
    def __init__(self, task_id):
        super().__init__(task_id)
        self.interactor = None
        self.interactor_exe = None

    def get_files_to_compile(self):
        super().get_files_to_compile()
        interactors = package_util.get_files_matching_pattern(self.task_id, f'{self.task_id}soc.*')
        if interactors:
            self.interactor = interactors[0]
            self.interactor_exe = paths.get_executables_path(package_util.get_executable(self.interactor))
            return [("interactor", [self.interactor], {})]

    def _get_interactor_result_file(self, sol_result_file_path: str):
        dirname = os.path.dirname(sol_result_file_path)
        basename_no_ext = os.path.basename(sol_result_file_path).split(".")[0]
        ext = os.path.basename(sol_result_file_path).split(".")[1]
        return os.path.join(dirname, f"{basename_no_ext}_interactor.{ext}")

    def check_output(self, input_file, output_file_path, output, answer_file_path) -> Tuple[bool, int]:
        with open(output_file_path, "r") as output_file:
            output = output_file.read().splitlines()
        return self._parse_checker_output(output)

    def _update_result_RE(self, result, program_exit_code):
        if program_exit_code == signal.Signals.SIGPIPE:
            result.Error = "Interactor exited prematurely"

    def _parse_additional_time(self, result_file_path) -> Union[ExecutionResult, None]:
        result, program_exit_code = self._parse_time_output(
            self._get_interactor_result_file(result_file_path)
        )
        if program_exit_code is not None and program_exit_code != 0:
            result.Status = Status.RE
            if program_exit_code == signal.Signals.SIGPIPE:
                result.Error = "Solution exited prematurely"
            else:
                result.Error = f"Program exited with code {program_exit_code}."
            return result
        return None

    def _run_program_time(self, command, env, executable, result_file_path, input_file_path, output_file_path,
                          answer_file_path, time_limit, memory_limit, hard_time_limit, execution_dir):
        r1, w1 = os.pipe()
        r2, w2 = os.pipe()
        for fd in (r1, w1, r2, w2):
            os.set_inheritable(fd, True)

        command_sol = self._wrap_with_time(
            [f'"{executable}"'],
            result_file_path
        )
        command_interactor = self._wrap_with_time(
            [f'"{self.interactor_exe}"', f'"{input_file_path}"', f'"{answer_file_path}"'],
            self._get_interactor_result_file(result_file_path)
        )

        def thread_wrapper(result, *args, **kwargs):
            result.append(self._run_subprocess(*args, **kwargs))

        with open(output_file_path, "w") as output_file:
            sol_result = []
            solution = Thread(
                target=thread_wrapper,
                args=(sol_result, False, False, executable, memory_limit, hard_time_limit, ' '.join(command_sol),),
                kwargs={
                    "shell": True,
                    "stdin": r1,
                    "stdout": w2,
                    "preexec_fn": os.setsid,
                    "cwd": execution_dir,
                    "pass_fds": (r1, w2,)
                }
            )
            interactor_result = []
            interactor = Thread(
                target=thread_wrapper,
                args=(interactor_result, False, False, self.interactor_exe, memory_limit, hard_time_limit,
                      ' '.join(command_interactor),),
                kwargs={
                    "shell": True,
                    "stdin": r2,
                    "stdout": w1,
                    "stderr": output_file,
                    "preexec_fn": os.setsid,
                    "cwd": execution_dir,
                    "pass_fds": (r2, w1,)
                }
            )
            solution.start()
            interactor.start()
            for fd in (r1, w1, r2, w2):
                os.close(fd)
            solution.join()
            interactor.join()

        return sol_result[0][0], sol_result[0][1]
