import os
import re
import subprocess
from typing import List, Tuple, Union

from sinol_make.programs.program import Program


class Ingen(Program):
    def get_name(self) -> str:
        return "ingen"

    def _regex_matches(self) -> List[re.Pattern]:
        return [
            re.compile(r'%singen\.sh' % self.task_id),
            re.compile(r'%singen\.(cpp|cc|java|py|pas)' % self.task_id),
            re.compile(r'%singen.*\.(cpp|cc|java|py|pas|sh)' % self.task_id),
        ]

    def _regex_match(self) -> re.Pattern:
        return re.compile(r'%singen.*\.(cpp|cc|java|py|pas|sh)' % self.task_id)

    def get_dir(self) -> str:
        return "prog"

    def _use_fsanitize(self) -> bool:
        return True

    def is_shell_ingen(self) -> bool:
        return os.path.splitext(self.file_path)[1] == '.sh'

    def compile(self) -> Tuple[Union[str, None], str]:
        if self.is_shell_ingen():
            self.executable_path = self.file_path
            st = os.stat(self.file_path)
            os.chmod(self.file_path, st.st_mode | 0o111)
            return self.file_path, ''
        else:
            return super().compile()

    def run(self, cwd=None) -> int:
        if cwd is None:
            cwd = os.path.join(os.getcwd(), "in")
        exit_code = super().run(stderr=subprocess.STDOUT, cwd=cwd, shell=True)
        return exit_code == 0
