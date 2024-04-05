import os
import tempfile

from sinol_make.helpers import compile, paths
from sinol_make.helpers import cache
from sinol_make.structs.cache_structs import CacheFile, CacheTest
from sinol_make.structs.status_structs import ExecutionResult, Status


def test_compilation_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        program = os.path.join(tmpdir, 'program.cpp')
        open(program, 'w').write('int main() { return 0; }')

        assert cache.check_compiled(program, "default", False) is None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path = cache.check_compiled(program, "default", False)
        assert exe_path is not None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path2 = cache.check_compiled(program, "default", False)
        assert exe_path2 == exe_path

        open(program, 'w').write('int main() { return 1; }')
        assert cache.check_compiled(program, "default", False) is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert cache.check_compiled(program, "default", False) is not None

        open(program, 'w').write('int main() { return 0; }')
        assert cache.check_compiled(program, "default", False) is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert cache.check_compiled(program, "default", False) is not None

        assert cache.check_compiled(program, "default", True) is None
        cache.save_compiled(program, exe_path, "default", True)
        assert cache.check_compiled(program, "default", True) is not None

        assert cache.check_compiled(program, "oioioi", True) is None
        cache.save_compiled(program, exe_path, "oioioi", True)
        assert cache.check_compiled(program, "oioioi", True) is not None


def test_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        assert cache.get_cache_file("abc.cpp") == CacheFile()

        cache_file = CacheFile(
            md5sum="md5sum",
            executable_path="abc.e",
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

        with open("abc.cpp", "w") as f:
            f.write("int main() { return 0; }")
        cache_file.save("abc.cpp")
        assert cache.get_cache_file("abc.cpp") == cache_file
        cache.save_compiled("abc.cpp", "abc.e", "default", False,
                            is_checker=True)
        assert cache.get_cache_file("abc.cpp").tests == {}

        # Test that cache is cleared when extra compilation files change
        cache_file.save("abc.cpp")
        os.mkdir("prog")
        with open("prog/abclib.cpp", "w") as f:
            f.write("int main() { return 0; }")

        cache.process_extra_compilation_files(["abclib.cpp"], "abc")
        assert cache.get_cache_file("/some/very/long/path/abc.cpp") == CacheFile()
        assert cache.get_cache_file("abclib.cpp") != CacheFile()

        cache_file.save("abc.cpp")
        cache_file.save("abc.py")
        with open("prog/abclib.cpp", "w") as f:
            f.write("/* Changed file */ int main() { return 0; }")
        cache.process_extra_compilation_files(["abclib.cpp"], "abc")
        assert not os.path.exists(paths.get_cache_path("md5sums", "abc.cpp"))
        assert os.path.exists(paths.get_cache_path("md5sums", "abc.py"))
        assert cache.get_cache_file("abc.py") == cache_file
        assert cache.get_cache_file("abc.cpp") == CacheFile()

        # Test if after changing contest type all cached test results are removed
        cache_file.save("abc.cpp")
        cache_file.save("abc.py")

        cache.remove_results_if_contest_type_changed("default")
        assert cache.get_cache_file("abc.py") == cache_file
        assert cache.get_cache_file("abc.cpp") == cache_file

        cache.remove_results_if_contest_type_changed("oi")
        assert cache.get_cache_file("abc.py").tests == {}
        assert cache.get_cache_file("abc.cpp").tests == {}
