import yaml
import stat
import glob
import pytest
import tarfile
import zipfile
import tempfile

from sinol_make import configure_parsers
from sinol_make import util as sinol_util
from sinol_make.commands.doc import Command as DocCommand
from tests import util
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


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_library_package_path(),
                                            util.get_library_string_args_package_path(),
                                            util.get_shell_ingen_pack_path(), util.get_handwritten_package_path()],
                         indirect=True)
def test_simple(create_package, capsys):
    """
    Test exporting to archive.
    """
    package_path = create_package
    parser = configure_parsers()
    args = parser.parse_args(["export"])
    command = Command()
    command.run(args)

    task_id = package_util.get_task_id()
    out = capsys.readouterr().out
    _test_archive(package_path, out, f'{task_id}.tgz')


@pytest.mark.parametrize("create_package", [util.get_doc_package_path()], indirect=True)
def test_doc_cleared(create_package):
    """
    Test if files in `doc` directory are cleared.
    """
    parser = configure_parsers()
    args = parser.parse_args(["doc"])
    command = DocCommand()
    command.run(args)
    args = parser.parse_args(["export"])
    command = Command()
    command.run(args)

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

    parser = configure_parsers()
    args = parser.parse_args(["export"])
    command = Command()
    command.run(args)
    task_id = package_util.get_task_id()

    with tempfile.TemporaryDirectory() as tmpdir:
        with tarfile.open(f'{task_id}.tgz', "r") as tar:
            sinol_util.extract_tar(tar, tmpdir)

        shell_ingen = os.path.join(tmpdir, task_id, 'prog', f'{task_id}ingen.sh')
        assert os.path.exists(shell_ingen)
        st = os.stat(shell_ingen)
        assert st.st_mode & stat.S_IEXEC


@pytest.mark.parametrize("create_package", [util.get_handwritten_package_path()], indirect=True)
def test_handwritten_tests(create_package):
    """
    Test if handwritten tests are correctly copied.
    """
    parser = configure_parsers()
    args = parser.parse_args(["export"])
    command = Command()
    command.run(args)
    task_id = package_util.get_task_id()

    with tempfile.TemporaryDirectory() as tmpdir:
        with tarfile.open(f'{task_id}.tgz', "r") as tar:
            sinol_util.extract_tar(tar, tmpdir)

        extracted = os.path.join(tmpdir, task_id)
        for file in ["in/hwr0.in", "in/hwr0a.in", "out/hwr0.out", "out/hwr0a.out"]:
            assert os.path.exists(os.path.join(extracted, file))


@pytest.mark.parametrize("create_package", [util.get_ocen_package_path()], indirect=True)
def test_ocen_archive(create_package):
    """
    Test creation of ocen archive.
    """
    parser = configure_parsers()
    args = parser.parse_args(["export"])
    command = Command()
    command.run(args)
    task_id = package_util.get_task_id()
    in_handwritten = ["ocen0.in", "ocen0a.in", "ocen1a.in", "ocen1ocen.in"]
    out_handwritten = ["ocen0.out"]
    ocen_tests = ["ocen0", "ocen0a", "ocen0b", "ocen1ocen", "ocen2ocen"]

    with tempfile.TemporaryDirectory() as tmpdir:
        package_path = os.path.join(tmpdir, task_id)
        os.mkdir(package_path)
        with tarfile.open(f'{task_id}.tgz', "r") as tar:
            sinol_util.extract_tar(tar, tmpdir)

        for ext in ["in", "out"]:
            tests = [os.path.basename(f) for f in glob.glob(os.path.join(package_path, ext, f'*.{ext}'))]
            assert set(tests) == set(in_handwritten if ext == "in" else out_handwritten)

        ocen_archive = os.path.join(package_path, "attachments", f"{task_id}ocen.zip")
        assert os.path.exists(ocen_archive)
        ocen_dir = os.path.join(package_path, "ocen_dir")

        with zipfile.ZipFile(ocen_archive, "r") as zip:
            zip.extractall(ocen_dir)

        for ext in ["in", "out"]:
            tests = [os.path.basename(f) for f in glob.glob(os.path.join(ocen_dir, task_id, ext, f'*.{ext}'))]
            assert set(tests) == set([f'{test}.{ext}' for test in ocen_tests])
