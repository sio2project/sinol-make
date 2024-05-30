import os
import sys
import time
import signal
import psutil
import subprocess
from typing import List, Dict, Any, Tuple, Union

from sinol_make import util
from sinol_make.interfaces.Errors import CheckerOutputException
from sinol_make.structs.status_structs import ExecutionResult, Status


class BaseTaskType:
    def __init__(self, task_id):
        self.task_id = task_id
        self._has_checker = False

    def run_outgen(self):
        return True

    def require_outputs(self):
        return True

    def get_files_to_compile(self) -> List[Tuple[str, List[str], Dict[str, Any]]]:
        """
        Returns a list of tuples where:
         - the first element is what will be printed in `Compiling {first_element}`
         - the second element is a list of *args passed to `run.compile`
         - the third element is a dictionary of **kwargs passed to `run.compile`
        """
        pass

    def has_checker(self) -> bool:
        return self._has_checker

    def _run_checker(self, input_file, output_file_path, answer_file_path) -> List[str]:
        return []

    def _raise_empty_output(self):
        raise CheckerOutputException("Checker output is empty.")

    def _parse_checker_output(self, checker_output: List[str]) -> Tuple[bool, int]:
        """
        Parse the output of the checker
        :return: tuple of (is_correct, score)
        """
        if len(checker_output) == 0:
            raise CheckerOutputException("Checker output is empty.")

        if checker_output[0].strip() == "OK":
            points = 100
            if len(checker_output) >= 3:
                try:
                    points = int(checker_output[2].strip())
                except ValueError:
                    pass

            return True, points
        else:
            return False, 0

    def check_output(self, input_file, output_file_path, output, answer_file_path) -> Tuple[bool, int]:
        if self._has_checker:
            with open(output_file_path, "w") as output_file:
                output_file.write("\n".join(output) + "\n")
            checker_output = self._run_checker(input_file, output_file_path, answer_file_path)
            return self._parse_checker_output(checker_output)
        else:
            with open(answer_file_path, "r") as answer_file:
                correct = util.lines_diff(output, answer_file.readlines())
            return correct, 100 if correct else 0

    def _prepare_oiejq_env(self, env: Dict[str, str], memory_limit) -> Dict[str, str]:
        env['MEM_LIMIT'] = f'{memory_limit}K'
        env['MEASURE_MEM'] = '1'
        env['UNDER_OIEJQ'] = '1'
        return env

    def _wrap_with_oiejq(self, command: str, oiejq_path: str) -> str:
        return f'"{oiejq_path}" {command}'

    def _wrap_with_time(self, command: List[str], result_file_path: str) -> List[str]:
        if sys.platform == 'darwin':
            time_name = 'gtime'
        elif sys.platform == 'linux':
            time_name = '/usr/bin/time'
        elif sys.platform == 'win32' or sys.platform == 'cygwin':
            raise Exception("Measuring time with GNU time on Windows is not supported.")
        else:
            raise Exception(f"Unknown platform: {sys.platform}")

        return [time_name, '-f', '%U\\\\n%M\\\\n%x', '-o', f'"{result_file_path}"'] + command

    def _parse_time_output(self, result_file_path: str):
        result = ExecutionResult()
        program_exit_code = 0
        with open(result_file_path, "r") as result_file:
            lines = result_file.readlines()
        if len(lines) == 3:
            """
            If programs runs successfully, the output looks like this:
             - first line is CPU time in seconds
             - second line is memory in KB
             - third line is exit code
            This format is defined by -f flag in time command.
            """
            result.Time = round(float(lines[0].strip()) * 1000)
            result.Memory = int(lines[1].strip())
            program_exit_code = int(lines[2].strip())
        elif len(lines) > 0 and ("Command terminated by signal " in lines[0] or "Command exited with non-zero status" in lines[0]):
            """
            If there was a runtime error, the first line is the error message with signal number.
            For example:
                Command terminated by signal 11
            or
                Command exited with non-zero status 1
            """
            program_exit_code = int(lines[0].strip().split(" ")[-1])
        else:
            result.Status = Status.RE
            result.Error = "Unexpected output from time command: " + "".join(lines)
        return result, program_exit_code

    def _parse_time(self, time_str):
        if len(time_str) < 3: return -1
        return int(time_str[:-2])

    def _parse_memory(self, memory_str):
        if len(memory_str) < 3: return -1
        return int(memory_str[:-2])

    def _parse_oiejq_output(self, result_file_path: str):
        result = ExecutionResult()
        with open(result_file_path, "r") as result_file:
            for line in result_file:
                line = line.strip()
                if ": " in line:
                    (key, value) = line.split(": ")[:2]
                    if key == "Time":
                        result.Time = self._parse_time(value)
                    elif key == "Memory":
                        result.Memory = self._parse_memory(value)
                    else:
                        setattr(result, key, value)
        return result

    def _run_subprocess(self, oiejq: bool, sigint_handler, executable, memory_limit, hard_time_limit, *args, **kwargs):
        process = subprocess.Popen(*args, **kwargs)
        if 'pass_fds' in kwargs:
            for fd in kwargs['pass_fds']:
                os.close(fd)

        if sigint_handler:
            def sigint_handler(signum, frame):
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
                sys.exit(1)

            signal.signal(signal.SIGINT, sigint_handler)
        timeout = False
        mem_limit_exceeded = False

        if oiejq:
            mem_limit_exceeded = False
            try:
                process.wait(timeout=hard_time_limit)
            except subprocess.TimeoutExpired:
                timeout = True
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
                process.communicate()
        else:  # time
            start_time = time.time()
            while process.poll() is None:
                try:
                    time_process = psutil.Process(process.pid)
                    executable_process = None
                    for child in time_process.children():
                        if child.name() == executable:
                            executable_process = child
                            break
                    if executable_process is not None and executable_process.memory_info().rss > memory_limit * 1024:
                        try:
                            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        mem_limit_exceeded = True
                        break
                except psutil.NoSuchProcess:
                    pass

                if time.time() - start_time > hard_time_limit:
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    timeout = True
                    break

        return timeout, mem_limit_exceeded

    def _run_program_oiejq(self, command, env, executable, result_file_path, input_file_path, output_file_path,
                           answer_file_path, time_limit, memory_limit, hard_time_limit, execution_dir):
        raise NotImplementedError()

    def _run_program_time(self, command, env, executable, result_file_path, input_file_path, output_file_path,
                          answer_file_path, time_limit, memory_limit, hard_time_limit, execution_dir):
        raise NotImplementedError()

    def _parse_additional_time(self, result_file_path) -> Union[ExecutionResult, None]:
        return None

    def run(self, oiejq: bool, timetool_path, executable, result_file_path, input_file_path, output_file_path,
            answer_file_path, time_limit, memory_limit, hard_time_limit, execution_dir) -> ExecutionResult:
        env = os.environ.copy()
        result = ExecutionResult()
        if oiejq:
            timeout, mem_limit_exceeded = self._run_program_oiejq(timetool_path, env, executable, result_file_path,
                                                                  input_file_path, output_file_path, answer_file_path,
                                                                  time_limit, memory_limit, hard_time_limit,
                                                                  execution_dir)
            result = self._parse_oiejq_output(result_file_path)
        else:
            timeout, mem_limit_exceeded = self._run_program_time(timetool_path, env, executable, result_file_path,
                                                                 input_file_path, output_file_path, answer_file_path,
                                                                 time_limit, memory_limit, hard_time_limit,
                                                                 execution_dir)
            if not timeout:
                result, program_exit_code = self._parse_time_output(result_file_path)
                if program_exit_code is not None and program_exit_code != 0 and result.Status != Status.RE:
                    result.Status = Status.RE
                    result.Error = f"Program exited with code {program_exit_code}."
                    return result

        try:
            with open(output_file_path, "r") as output_file:
                output = output_file.readlines()
        except FileNotFoundError:
            output = []

        def getattrd(obj, attr, default):
            if getattr(obj, attr, None) is None:
                return default
            return getattr(obj, attr)

        if result.Status == Status.RE:
            return result
        if timeout:
            result.Status = Status.TL
        elif mem_limit_exceeded:
            result.Status = Status.ML
            result.Memory = memory_limit + 1  # Add one so that the memory is red in the table
        elif getattrd(result, 'Time', 0) > time_limit:
            result.Status = Status.TL
        elif getattrd(result, 'Memory', 0) > memory_limit:
            result.Status = Status.ML
        else:
            try:
                correct, result.Points = self.check_output(input_file_path, output_file_path, output, answer_file_path)
                if correct:
                    result.Status = Status.OK
                else:
                    result.Status = Status.WA
            except CheckerOutputException as e:
                result.Status = Status.RE
                result.Error = str(e)

        return result
