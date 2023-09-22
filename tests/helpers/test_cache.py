import os
import tempfile

from sinol_make.helpers import compile
from sinol_make.helpers import cache
from sinol_make.structs.cache_structs import CacheFile, CacheTest
from sinol_make.structs.status_structs import ExecutionResult, Status


def test_compilation_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        program = os.path.join(tmpdir, 'program.cpp')
        open(program, 'w').write('int main() { return 0; }')

        assert cache.check_compiled(program) is None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path = cache.check_compiled(program)
        assert exe_path is not None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path2 = cache.check_compiled(program)
        assert exe_path2 == exe_path

        open(program, 'w').write('int main() { return 1; }')
        assert cache.check_compiled(program) is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert cache.check_compiled(program) is not None

        open(program, 'w').write('int main() { return 0; }')
        assert cache.check_compiled(program) is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert cache.check_compiled(program) is not None


def test_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        assert cache.get_cache_file("program.cpp") == CacheFile()

        cache_file = CacheFile(
            md5sum="md5sum",
            executable_path="program.e",
            tests={
                "md5sum1": CacheTest(
                    time_limit=1000,
                    memory_limit=1024,
                    time_tool="time",
                    result=ExecutionResult(
                        status=Status.OK,
                        Time=0.5,
                        Memory=512,
                        Points=10,
                    )
                ),
                "md5sum2": CacheTest(
                    time_limit=2000,
                    memory_limit=2048,
                    time_tool="time",
                    result=ExecutionResult(
                        status=Status.OK,
                        Time=1,
                        Memory=1024,
                        Points=20,
                    )
                ),
            }
        )

        with open("program.cpp", "w") as f:
            f.write("int main() { return 0; }")
        cache_file.save("program.cpp")
        assert cache.get_cache_file("program.cpp") == cache_file
        cache.save_compiled("program.cpp", "program.e", is_checker=True)
        assert cache.get_cache_file("program.cpp").tests == {}
