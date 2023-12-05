import os
import re
import hashlib


class Test:
    def __init__(self, task_id: str, file_path: str, exists: bool = True):
        self.task_id = task_id
        if exists:
            self.file_path = self._find(file_path)
            self.md5 = self.get_md5()
        else:
            self.file_path = os.path.abspath(os.path.join(self.get_dir(), os.path.basename(file_path)))
        self.basename = os.path.basename(self.file_path)
        self.test_id = os.path.splitext(self.basename)[0][len(self.task_id):]
        if self.test_id.endswith('ocen'):
            self.group = 0
        else:
            self.group = int("".join(filter(str.isdigit, self.test_id)))

    def __eq__(self, other):
        return self.file_path == other.file_path

    def __lt__(self, other):
        return (self.group, self.test_id) < (other.group, other.test_id)

    def __hash__(self):
        return hash(self.file_path)

    def __str__(self):
        return f"<{self.get_type()} test {self.basename}>"

    def __repr__(self):
        return str(self)

    def get_type(self) -> str:
        raise NotImplementedError()

    def get_dir(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def _regex_match_static(task_id: str) -> re.Pattern:
        raise NotImplementedError()

    def _regex_match(self) -> re.Pattern:
        return self._regex_match_static(self.task_id)

    def _find(self, file_path: str):
        basename = os.path.basename(file_path)
        if self._regex_match().match(basename) is not None:
            abspath = os.path.abspath(file_path)
            if os.path.exists(abspath):
                return abspath
            abspath = os.path.abspath(os.path.join(self.get_dir(), basename))
            if os.path.exists(abspath):
                return abspath
            raise FileNotFoundError(f'File {file_path} does not exist.')
        raise FileNotFoundError(f'File {file_path} does not exist or is not a {self.get_type()} test.')

    class ctx_manager:
        def __init__(self, test: "Test", mode: str = 'r'):
            self.test = test
            self.mode = mode

        def __enter__(self):
            self.file = open(self.test.file_path, self.mode)
            return self.file

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.file.close()
            if "w" in self.mode:
                self.test.md5 = self.test.get_md5()

    def open(self, mode: str = 'r') -> "ctx_manager":
        return self.ctx_manager(self, mode)

    def get_md5(self) -> str:
        with open(self.file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def exists(self) -> bool:
        return os.path.exists(self.file_path)

    def remove(self):
        os.unlink(self.file_path)
