import re
from typing import List, Union, Tuple

from sinol_make.programs.program import Program
from sinol_make.tests.input import InputTest


class Inwer(Program):
    def __init__(self, executor, compiler_manager, task_id, file_path = None, executable_name = None):
        super().__init__(executor, compiler_manager, task_id, file_path, executable_name)
        self.test_name = None

    def get_name(self) -> str:
        return "inwer"

    def _regex_matches(self) -> List[re.Pattern]:
        return [
            re.compile(r'%sinwer\.(cpp|cc|java|py|pas)' % self.task_id),
            re.compile(r'%sinwer.*\.(cpp|cc|java|py|pas)' % self.task_id),
        ]

    def _regex_match(self) -> re.Pattern:
        return re.compile(r'%sinwer.*\.(cpp|cc|java|py|pas)' % self.task_id)

    def get_dir(self) -> str:
        return "prog"

    def _use_fsanitize(self) -> bool:
        return True

    def _run_arguments(self) -> List[str]:
        if self.test_name is None:
            raise ValueError("Test name not set")
        return [self.executable_path, self.test_name]

    def run(self, test: InputTest, stdin = None, stdout = None, stderr = None,
            cwd = None, return_out = False, shell = False) -> Union[int, Tuple[int, bytes, bytes]]:
        self.test_name = test.basename
        return super().run(stdin, stdout, stderr, cwd, return_out, shell)
