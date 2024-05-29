import os
import signal
from threading import Thread
from typing import Tuple, Union

from sinol_make import oiejq
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

    def _check_errors(self, result, interactor_exit_code, program_exit_code):
        if interactor_exit_code != 0 and interactor_exit_code != signal.Signals.SIGPIPE:
            result.Status = Status.RE
            result.Error = f"Interactor exited with code {interactor_exit_code}."
            return result
        elif program_exit_code != 0 and program_exit_code != signal.Signals.SIGPIPE:
            result.Status = Status.RE
            result.Error = f"Solution exited with code {program_exit_code}."
            return result
        elif interactor_exit_code == signal.Signals.SIGPIPE:
            result.Status = Status.RE
            result.Error = "Interactor exited prematurely"
            return result
        else:
            return None

    def _parse_additional_time(self, result_file_path) -> Union[ExecutionResult, None]:
        result, program_exit_code = self._parse_time_output(result_file_path)
        _, interactor_exit_code = self._parse_time_output(
            self._get_interactor_result_file(result_file_path)
        )
        return self._check_errors(result, interactor_exit_code, program_exit_code)

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
            [f'"{self.interactor_exe}"', f'"{input_file_path}"', f'"{output_file_path}"'],
            self._get_interactor_result_file(result_file_path)
        )

        def thread_wrapper(result, *args, **kwargs):
            result.append(self._run_subprocess(*args, **kwargs))

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
                "pass_fds": (r1, w2,),
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
                "preexec_fn": os.setsid,
                "cwd": execution_dir,
                "pass_fds": (r2, w1,)
            }
        )
        solution.start()
        interactor.start()
        solution.join()
        interactor.join()

        return sol_result[0][0], sol_result[0][1]

    def _wrap_with_sio2jail(self, command, result_file_path, sio2jail_path, mem_limit):
        return [f'"{sio2jail_path}"', "--mount-namespace", "off", "--pid-namespace", "off", "--uts-namespace", "off",
                "--ipc-namespace", "off", "--net-namespace", "off", "--capability-drop", "off",
                "--user-namespace", "off", "-s", "-m", str(mem_limit), "-f", "3", "-o", "oiaug", "--"] + \
                command + [f'3>"{result_file_path}"']

    def _run_program_oiejq(self, command, env, executable, result_file_path, input_file_path, output_file_path, answer_file_path, time_limit, memory_limit, hard_time_limit, execution_dir):
        r1, w1 = os.pipe()
        r2, w2 = os.pipe()
        for fd in (r1, w1, r2, w2):
            os.set_inheritable(fd, True)

        oiejq_path = oiejq.get_oiejq_path()
        sio2jail_path = os.path.join(os.path.dirname(oiejq_path), "sio2jail")
        command_sol = self._wrap_with_sio2jail(
            [f'"{executable}"'],
            result_file_path,
            sio2jail_path,
            memory_limit
        )

        command_interactor = self._wrap_with_sio2jail(
            [f'"{self.interactor_exe}"', f'"{input_file_path}"', f'"{output_file_path}"'],
            self._get_interactor_result_file(result_file_path),
            sio2jail_path,
            memory_limit
        )

        def thread_wrapper(result, *args, **kwargs):
            result.append(self._run_subprocess(*args, **kwargs))

        sol_result = []
        solution = Thread(
            target=thread_wrapper,
            args=(sol_result, True, False, executable, memory_limit, hard_time_limit, ' '.join(command_sol),),
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
            args=(interactor_result, True, False, self.interactor_exe, memory_limit, hard_time_limit,
                    ' '.join(command_interactor),),
            kwargs={
                "shell": True,
                "stdin": r2,
                "stdout": w1,
                "preexec_fn": os.setsid,
                "cwd": execution_dir,
                "pass_fds": (r2, w1,)
            }
        )
        solution.start()
        interactor.start()
        solution.join()
        interactor.join()

        print(open(self._get_interactor_result_file(result_file_path), "r").read())
        return sol_result[0][0], sol_result[0][1]

    def _parse_oiejq_output(self, result_file_path: str):
        result = ExecutionResult()
        with open(result_file_path, "r") as result_file:
            try:
                line = result_file.readline()
                status, code, time, _, mem, _ = line.split()
            except ValueError:
                result.Status = Status.RE
                result.Error = "Invalid output format: " + line
                return result

        with open(self._get_interactor_result_file(result_file_path), "r") as result_file:
            try:
                line = result_file.readline()
                status_interactor, code_interactor, time_interactor, _, mem_interactor, _ = line.split()
            except ValueError:
                result.Status = Status.RE
                result.Error = "Invalid interactor output format: " + line
                return result

        result = self._check_errors(result, int(code_interactor), int(code))
        result.Time = round(float(time * 1000))
        result.Memory = int(mem)
        return result

    def require_outputs(self):
        return False
