import os
import re
import signal
from threading import Thread
from typing import Tuple, List

from sinol_make.executors.detailed import DetailedExecutor
from sinol_make.helpers import package_util, paths
from sinol_make.interfaces.Errors import CheckerException
from sinol_make.structs.status_structs import ExecutionResult, Status
from sinol_make.task_type import BaseTaskType
from sinol_make import util


class InteractiveTaskType(BaseTaskType):
    INTERACTOR_MEMORY_LIMIT = 256 * 2 ** 10

    class Pipes:
        """
        Class for storing file descriptors for interactor and solution processes.
        """
        r_interactor = None
        w_interactor = None
        r_solution = None
        w_solution = None

        def __init__(self, r_interactor, w_interactor, r_solution, w_solution):
            """
            Constructor for Pipes class.
            :param r_interactor: file descriptor from which the interactor reads from the solution
            :param w_interactor: file descriptor to which the interactor writes to the solution
            :param r_solution: file descriptor from which the solution reads from the interactor
            :param w_solution: file descriptor to which the solution writes to the interactor
            """
            self.r_interactor = r_interactor
            self.w_interactor = w_interactor
            self.r_solution = r_solution
            self.w_solution = w_solution

    class ExecutionWrapper(Thread):
        def __init__(self, executor, *args, **kwargs):
            super().__init__()
            self.executor = executor
            self.args = args
            self.kwargs = kwargs
            self.result = None
            self.exception = None

        def run(self):
            try:
                self.result = self.executor.execute(*self.args, **self.kwargs)
            except Exception as e:
                self.exception = e

    @staticmethod
    def get_interactor_re(task_id: str) -> re.Pattern:
        """
        Returns regex pattern matching all solutions for given task.
        :param task_id: Task id.
        """
        return re.compile(r"^%ssoc\.(c|cpp|cc|py)$" % task_id)

    @classmethod
    def identify(cls) -> Tuple[bool, int]:
        task_id = package_util.get_task_id()
        for file in os.listdir(os.path.join(os.getcwd(), "prog")):
            if cls.get_interactor_re(task_id).match(file):
                return True, 10
        return False, 0

    @staticmethod
    def name() -> str:
        return "interactive"

    def __init__(self, timetool, sio2jail_path):
        super().__init__(timetool, sio2jail_path)
        self.has_checker = False
        self.interactor = None
        self.interactor_executor = DetailedExecutor()

    def additional_files_to_compile(self) -> List[Tuple[str, str, str, bool, bool]]:
        ret = []
        task_id = package_util.get_task_id()
        interactor = package_util.get_files_matching_pattern(task_id, f'{task_id}soc.*')
        if len(interactor) > 0:
            interactor = interactor[0]
            interactor_basename = os.path.basename(interactor)
            self.interactor = paths.get_executables_path(interactor_basename + ".e")
            ret += [(interactor, self.interactor, "interactor", True, True)]
        else:
            util.exit_with_error(f"Interactor not found for task {task_id} (how did you manage to do this????)")
        return ret

    @staticmethod
    def run_outgen() -> bool:
        # In interactive tasks via IO output files don't exist.
        return False

    @staticmethod
    def allow_chkwer() -> bool:
        # Probably could be implemented but sounds painful.
        return False

    def _fill_result(self, result: ExecutionResult, iresult: ExecutionResult, interactor_output: List[str]):
        sol_sig = result.ExitSignal
        inter_sig = iresult.ExitSignal

        if interactor_output[0] != '':
            try:
                ok, points, comment = self._parse_checker_output(interactor_output)
            except CheckerException as e:
                result.Status = Status.RE
                result.Error = str(e)
                result.Fail = True
                return
            result.Points = float(points)
            result.Comment = comment
            if ok:
                result.Status = Status.OK
            else:
                result.Status = Status.WA
            result.Error = None
        elif iresult.Status != Status.OK and iresult.Status != Status.TL and inter_sig != signal.SIGPIPE:
            result.Status = Status.RE
            result.Error = (f"Interactor got {iresult.Status}. This would cause SE on sio. "
                            f"Interactor error: '{iresult.Error}'. "
                            f"Interactor stderr: {iresult.Stderr}. "
                            f"Interactor output: {interactor_output}")
            result.Fail = True
        elif result.Status is not None and result.Status != Status.OK and sol_sig != signal.SIGPIPE:
            return
        elif inter_sig == signal.SIGPIPE:
            result.Status = Status.WA
            result.Comment = "Solution exited prematurely"
        elif iresult == Status.TL:
            result.Status = Status.TL
            result.Comment = "interactor time limit exceeded (user's solution or interactor can be the cause)"
        else:
            result.Status = Status.RE
            result.Error = "Unexpected interactor error. Create an issue."
            result.Fail = True

    def run(self, time_limit, hard_time_limit, memory_limit, input_file_path, output_file_path, answer_file_path,
            result_file_path, executable, execution_dir) -> ExecutionResult:
        config = package_util.get_config()
        num_processes = config.get('num_processes', 1)
        proc_pipes = []

        file_no_ext = os.path.splitext(result_file_path)[0]
        interactor_res_file = file_no_ext + "-soc.res"
        processes_res_files = [file_no_ext + f"-{i}.res" for i in range(num_processes)]

        for _ in range(num_processes):
            r1, w1 = os.pipe()
            r2, w2 = os.pipe()
            for fd in (r1, w1, r2, w2):
                os.set_inheritable(fd, True)
            proc_pipes.append(self.Pipes(r1, w2, r2, w1))

        interactor_args = [str(num_processes)]
        for pipes in proc_pipes:
            interactor_args.extend([str(pipes.r_interactor), str(pipes.w_interactor)])

        processes = []
        interactor_fds = []
        for pipes in proc_pipes:
            interactor_fds.extend([pipes.r_interactor, pipes.w_interactor])

        with open(input_file_path, "r") as inf, open(output_file_path, "w") as outf:
            interactor = self.ExecutionWrapper(
                self.interactor_executor,
                [f'"{self.interactor}"'] + interactor_args,
                time_limit * 2,
                hard_time_limit * 2,
                memory_limit,
                interactor_res_file,
                self.interactor,
                execution_dir,
                stdin=inf,
                stdout=outf,
                fds_to_close=interactor_fds,
                pass_fds=interactor_fds,
            )

            for i in range(num_processes):
                pipes = proc_pipes[i]
                proc = self.ExecutionWrapper(
                    self.executor,
                    [f'"{executable}"', str(i)],
                    time_limit,
                    hard_time_limit,
                    memory_limit,
                    processes_res_files[i],
                    executable,
                    execution_dir,
                    stdin=pipes.r_solution,
                    stdout=pipes.w_solution,
                    fds_to_close=[pipes.r_solution, pipes.w_solution],
                )
                processes.append(proc)

            for proc in processes:
                proc.start()
            interactor.start()

            for proc in processes:
                proc.join()
            interactor.join()

            result = ExecutionResult(Time=0, Memory=0)
            if interactor.exception:
                result.RE = True
                result.Error = f"Interactor got an exception:\n" + str(interactor.exception)
            for i in range(num_processes):
                proc = processes[i]
                if proc.exception:
                    result.RE = True
                    result.Error = f"Solution {i} got an exception:\n" + str(proc.exception)

            for proc in processes:
                if proc.result.Status != Status.OK:
                    result = proc.result
                    break
                result.Time = max(result.Time, proc.result.Time)
                result.Memory = max(result.Memory, proc.result.Memory)

            iresult = interactor.result

        try:
            with open(output_file_path, "r") as ires_file:
                interactor_output = [line.rstrip() for line in ires_file.readlines()]
            while len(interactor_output) < 3:
                interactor_output.append("")
        except FileNotFoundError:
            interactor_output = []

        self._fill_result(result, iresult, interactor_output)
        return result
