import os
import tempfile

import yaml

from sinol_make import util
from sinol_make.helpers import compile, package_util, paths
from sinol_make.helpers import cache
from sinol_make.structs.cache_structs import CacheFile, CacheTest
from sinol_make.structs.status_structs import ExecutionResult, Status


def test_compilation_caching():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        cache.create_cache_dirs()
        program = os.path.join(tmpdir, 'program.cpp')
        open(program, 'w').write('int main() { return 0; }')

        assert cache.check_compiled(program, "default", "no") is None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path = cache.check_compiled(program, "default", "no")
        assert exe_path is not None

        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        exe_path2 = cache.check_compiled(program, "default", "no")
        assert exe_path2 == exe_path

        open(program, 'w').write('int main() { return 1; }')
        assert cache.check_compiled(program, "default", "no") is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert cache.check_compiled(program, "default", "no") is not None

        open(program, 'w').write('int main() { return 0; }')
        assert cache.check_compiled(program, "default", "no") is None
        assert compile.compile(program, os.path.join(tmpdir, 'program'), compile_log=None)
        assert cache.check_compiled(program, "default", "no") is not None

        assert cache.check_compiled(program, "default", "simple") is None
        cache.save_compiled(program, exe_path, "default", "simple")
        assert cache.check_compiled(program, "default", "simple") is not None

        assert cache.check_compiled(program, "oioioi", "simple") is None
        cache.save_compiled(program, exe_path, "oioioi", "simple")
        assert cache.check_compiled(program, "oioioi", "simple") is not None


def test_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        cache.create_cache_dirs()
        assert cache.get_cache_file("abc.cpp") == CacheFile()

        cache_file = CacheFile(
            md5sum="md5sum",
            executable_path="abc.e",
            sanitizers='no',
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
                            clear_cache=True)
        assert cache.get_cache_file("abc.cpp").tests == {}

        # Test if after changing contest type all cached test results are removed
        cache_file.save("abc.cpp")
        cache_file.save("abc.py")

        cache.remove_results_if_contest_type_changed("default")
        assert cache.get_cache_file("abc.py") == cache_file
        assert cache.get_cache_file("abc.cpp") == cache_file

        cache.remove_results_if_contest_type_changed("oi")
        assert cache.get_cache_file("abc.py").tests == {}
        assert cache.get_cache_file("abc.cpp").tests == {}


def test_old_cache_file():
    """
    Test if cache files saved by versions of sinol-make which didn't store
    the extra compilation hash are still valid.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        cache.create_cache_dirs()
        program = os.path.join(tmpdir, 'program.cpp')
        open(program, 'w').write('int main() { return 0; }')
        exe_path = os.path.join(tmpdir, 'program')
        open(exe_path, 'w').write('')

        cache_file = CacheFile(md5sum=util.get_file_md5(program), executable_path=exe_path)
        contents = cache_file.to_dict()
        del contents["extra_compilation_hash"]
        with open(paths.get_cache_path("md5sums", "program.cpp"), "w") as f:
            yaml.dump(contents, f)

        assert cache.get_cache_file(program) == cache_file
        assert cache.check_compiled(program, "default", "no") == exe_path


def test_extra_compilation_files_caching():
    """
    Test if changing an extra compilation file invalidates the compilation cache.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        cache.create_cache_dirs()
        os.mkdir("prog")
        library = os.path.join(tmpdir, "prog", "abclib.cpp")
        open(library, 'w').write('int lib() { return 0; }\n')
        program = os.path.join(tmpdir, "prog", "abc.cpp")
        open(program, 'w').write('int lib();\nint main() { return lib(); }\n')
        output = os.path.join(tmpdir, "abc.e")

        def compile_program():
            return compile.compile(program, output, compile_log=None, extra_compilation_args=[library],
                                   extra_compilation_files=[library])

        def get_hash():
            return package_util.get_extra_compilation_hash("cpp", [library], [library])

        assert compile_program()
        assert cache.check_compiled(program, "default", "no", get_hash()) is not None
        # The executable can't be used when the library isn't compiled in.
        assert cache.check_compiled(program, "default", "no") is None
        # The library is copied next to the executable, so that it's always up to date.
        assert util.get_file_md5(os.path.join(tmpdir, "abclib.cpp")) == util.get_file_md5(library)

        previous_hash = get_hash()
        open(library, 'w').write('int lib() { return 0; } // Changed library.\n')
        assert get_hash() != previous_hash
        assert cache.check_compiled(program, "default", "no", get_hash()) is None

        assert compile_program()
        assert cache.check_compiled(program, "default", "no", get_hash()) is not None
        assert util.get_file_md5(os.path.join(tmpdir, "abclib.cpp")) == util.get_file_md5(library)

        # Extra compilation files in other languages don't affect compilation.
        assert package_util.get_extra_compilation_hash("py", [], [library]) == ""
        assert package_util.get_extra_compilation_hash("cpp", [], [library]) != ""
        # Header files affect compilation of C and C++ files.
        header = os.path.join(tmpdir, "prog", "abclib.h")
        open(header, 'w').write('int lib();\n')
        assert package_util.get_extra_compilation_hash("cpp", [], [header]) != ""
        assert package_util.get_extra_compilation_hash("c", [], [header]) != ""


def test_extra_compilation_args_caching():
    """
    Test if changing extra compilation arguments invalidates the compilation cache.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        cache.create_cache_dirs()
        program = os.path.join(tmpdir, 'program.cpp')
        open(program, 'w').write('int main() { return 0; }')
        output = os.path.join(tmpdir, 'program')

        assert compile.compile(program, output, compile_log=None)
        assert cache.check_compiled(program, "default", "no") is not None

        # Adding a compilation flag invalidates the cache.
        flag_hash = package_util.get_extra_compilation_hash("cpp", ["-DFOO"], [])
        assert flag_hash != ""
        assert cache.check_compiled(program, "default", "no", flag_hash) is None

        assert compile.compile(program, output, compile_log=None, extra_compilation_args=["-DFOO"])
        assert cache.check_compiled(program, "default", "no", flag_hash) is not None
        # Removing or changing the flag invalidates the cache again.
        assert cache.check_compiled(program, "default", "no") is None
        assert cache.check_compiled(
            program, "default", "no", package_util.get_extra_compilation_hash("cpp", ["-DBAR"], [])) is None
