import yaml
import stat
import glob
import pytest
import tarfile
import tempfile

from sinol_make import util as sinol_util
from sinol_make.commands.doc import Command as DocCommand
from sinol_make.commands.export import Command
from tests.fixtures import create_package
from .util import *


def _test_archive(package_path, out, tar):
    task_id = package_util.get_task_id()
    assert os.path.exists(tar)
    assert f'{tar}' in out

    with tempfile.TemporaryDirectory() as tmpdir:
        with tarfile.open(tar, "r") as tar:
            sinol_util.extract_tar(tar, tmpdir)

        extracted = os.path.join(tmpdir, task_id)
        assert os.path.exists(extracted)
        assert_configs_equal(package_path, extracted)
        assert_progs_equal(package_path, extracted)

        with open(os.path.join(package_path, "config.yml"), "r") as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
        with open(os.path.join(extracted, "makefile.in"), "r") as makefile:
            lines = makefile.readlines()
            assert_makefile_in(lines, task_id, config)

        if os.path.basename(package_path) == os.path.basename(util.get_handwritten_package_path()):
            for ext in ["in", "out"]:
                tests = [os.path.basename(f) for f in glob.glob(os.path.join(extracted, ext, f'*.{ext}'))]
                assert set(tests) == {f'hwr0.{ext}', f'hwr0a.{ext}'}
        else:
            assert glob.glob(os.path.join(extracted, "in", "*")) == []
            assert glob.glob(os.path.join(extracted, "out", "*")) == []


def run(arguments=None):
    util.run(Command, arguments)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_library_package_path(),
                                            util.get_library_string_args_package_path(),
                                            util.get_shell_ingen_pack_path(), util.get_handwritten_package_path()],
                         indirect=True)
def test_simple(create_package, capsys):
    """
    Test exporting to archive.
    """
    package_path = create_package
    run(["export"])

    task_id = package_util.get_task_id()
    out = capsys.readouterr().out
    _test_archive(package_path, out, f'{task_id}.tgz')


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_doc_cleared(create_package):
    """
    Test if files in `doc` directory are cleared.
    """
    util.run(DocCommand, ["doc"])
    run(["export"])

    with tempfile.TemporaryDirectory() as tmpdir:
        with tarfile.open(f'{package_util.get_task_id()}.tgz', "r") as tar:
            sinol_util.extract_tar(tar, tmpdir)

        extracted = os.path.join(tmpdir, package_util.get_task_id())
        assert os.path.exists(extracted)
        for pattern in ['doc/*~', 'doc/*.aux', 'doc/*.log', 'doc/*.dvi', 'doc/*.err', 'doc/*.inf']:
            assert glob.glob(os.path.join(extracted, pattern)) == []


@pytest.mark.parametrize("create_package", [util.get_shell_ingen_pack_path()], indirect=True)
def test_correct_permissions(create_package, capsys):
    """
    Checks if shell ingen has correct permissions.
    """
    shell_ingen = os.path.join(os.getcwd(), 'prog', f'{package_util.get_task_id()}ingen.sh')
    st = os.stat(shell_ingen)
    os.chmod(shell_ingen, st.st_mode & ~stat.S_IEXEC)

    run(["export"])
    task_id = package_util.get_task_id()

    with tempfile.TemporaryDirectory() as tmpdir:
        with tarfile.open(f'{task_id}.tgz', "r") as tar:
            sinol_util.extract_tar(tar, tmpdir)

        shell_ingen = os.path.join(tmpdir, task_id, 'prog', f'{task_id}ingen.sh')
        assert os.path.exists(shell_ingen)
        st = os.stat(shell_ingen)
        assert st.st_mode & stat.S_IEXEC
