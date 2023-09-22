import os
import tempfile

from sinol_make.helpers import compile
from sinol_make.helpers.cache import check_compiled, save_compiled


def test_compilation_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        program = os.path.join(tmpdir, 'program.cpp')
        open(program, 'w').write('int main() { return 0; }')

        assert check_compiled(program) is None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path = check_compiled(program)
        assert exe_path is not None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path2 = check_compiled(program)
        assert exe_path2 == exe_path

        open(program, 'w').write('int main() { return 1; }')
        assert check_compiled(program) is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert check_compiled(program) is not None

        open(program, 'w').write('int main() { return 0; }')
        assert check_compiled(program) is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert check_compiled(program) is not None
