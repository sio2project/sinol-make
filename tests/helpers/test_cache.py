import os
import tempfile

from sinol_make.helpers import compile


def test_compilation_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        program = os.path.join(tmpdir, 'program.cpp')
        open(program, 'w').write('int main() { return 0; }')

        assert compile.check_compiled(program) is None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path = compile.check_compiled(program) is not None
        assert exe_path is not None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path2 = compile.check_compiled(program)
        assert exe_path2 == exe_path

        open(program, 'w').write('int main() { return 1; }')
        assert compile.check_compiled(program) is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert compile.check_compiled(program) is not None

        open(program, 'w').write('int main() { return 0; }')
        assert compile.check_compiled(program) is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert compile.check_compiled(program) is not None
