import pytest
import tarfile
import tempfile

from sinol_make import configure_parsers
from tests import util
from tests.fixtures import create_package
from .util import *


def _test_deb(output_dir, out):
    task_id = package_util.get_task_id()
    deb = os.path.abspath(os.path.join(output_dir, f'oi-ocen-{task_id}.deb'))

    assert os.path.exists(deb)
    assert "Creating ocen debian package..." in out
    assert f'{deb}' in out

    # Extracting the .deb file
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        exit_code = os.system(f'dpkg-deb -X "{deb}" "{tmpdir}"')
        assert exit_code == 0
        exit_code = os.system(f'dpkg-deb -e "{deb}"')
        assert exit_code == 0

        control_dir = os.path.join(tmpdir, "DEBIAN")
        with open(os.path.join(control_dir, "postinst"), "r") as postinst_file:
            postinst = postinst_file.readlines()

            for line in postinst:
                if line.startswith('task_id ='):
                    assert line == f'task_id = "{task_id}"\n'
                    break

        ocen_tar = os.path.join(tmpdir, "usr", "share", f'oi-ocen-{task_id}', 'ocen-linux.tgz')
        tar_dir = os.path.join(tmpdir, "tar")
        with tarfile.open(ocen_tar, "r") as tar:
            tar.extractall(tar_dir)

        with open(os.path.join(tar_dir, "rozw", "oi.conf")) as oi_conf:
            lines = oi_conf.readlines()

        assert lines[0] == f'TASKS="{task_id}"\n'
        assert lines[1].startswith(f'TESTS_{task_id}=')

        tests = lines[1].split('=')[1].strip().strip('"').split(' ')
        if len(tests) == 1 and tests[0] == '':
            tests = []

        for test in tests:
            assert os.path.exists(os.path.join(tar_dir, "rozw", "in", f'{task_id}{test}.in'))
            assert os.path.exists(os.path.join(tar_dir, "rozw", "out", f'{task_id}{test}.out'))


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_handwritten_package_path(),
                                            util.get_shell_ingen_pack_path()], indirect=True)
def test_simple(create_package, capsys):
    """
    Test exporting to ocen debian package.
    """
    package_path = create_package
    parser = configure_parsers()
    args = parser.parse_args(["export", "--ocen"])
    command = Command()
    command.run(args)

    out = capsys.readouterr().out
    _test_deb(os.path.join(package_path, "export"), out)


@pytest.mark.parametrize("create_package", [util.get_simple_package_path(), util.get_handwritten_package_path()],
                            indirect=True)
def test_output_flag(create_package, capsys):
    """
    Test exporting to ocen debian package with output flag.
    """
    with tempfile.TemporaryDirectory() as output_dir:
        parser = configure_parsers()
        args = parser.parse_args(["export", "--ocen", "--output", output_dir])
        command = Command()
        command.run(args)

        out = capsys.readouterr().out
        _test_deb(output_dir, out)
