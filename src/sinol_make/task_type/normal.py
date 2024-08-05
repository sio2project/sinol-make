from typing import Tuple

from sinol_make.interfaces.Errors import CheckerException
from sinol_make.structs.status_structs import ExecutionResult, Status
from sinol_make.task_type import BaseTaskType


class NormalTaskType(BaseTaskType):
    @classmethod
    def identify(cls) -> Tuple[bool, int]:
        return True, 1

    @staticmethod
    def name() -> str:
        return "normal"

    def run(self, time_limit, hard_time_limit, memory_limit, input_file_path, output_file_path, answer_file_path,
            result_file_path, executable, execution_dir) -> ExecutionResult:
        with open(input_file_path, "r") as inf, open(output_file_path, "w") as outf:
            result = self.executor.execute([f'"{executable}"'], time_limit, hard_time_limit, memory_limit,
                                           result_file_path, executable, execution_dir, stdin=inf, stdout=outf)
        if result.Time > time_limit:
            result.Status = Status.TL
        elif result.Memory > memory_limit:
            result.Status = Status.ML
        elif result.Status == Status.OK:
            try:
                correct, points, comment = self.check_output(input_file_path, output_file_path, answer_file_path)
                result.Points = float(points)
                result.Comment = comment
                if not correct:
                    result.Status = Status.WA
            except CheckerException as e:
                result.Status = Status.RE
                result.Error = str(e)
                result.Fail = True
        return result
