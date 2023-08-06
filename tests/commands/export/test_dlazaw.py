import pytest
import tempfile

from sinol_make import configure_parsers
from tests import util
from tests.fixtures import create_package
from .util import *


def _test_deb(output_dir, out):
    deb = os.path.abspath(os.path.join(output_dir, f'oi-dlazaw.deb'))

    assert os.path.exists(deb)
    assert "Creating dlazaw debian package..." in out
    assert f'Exported to {deb}' in out

    # Extracting the .deb file
    with tempfile.TemporaryDirectory() as tmpdir:
        exit_code = os.system(f'dpkg-deb -X "{deb}" "{tmpdir}"')
        assert exit_code == 0

        test_file = os.path.join(tmpdir, "home", "zawodnik", "dlazaw", "testfile")
        assert os.path.exists(test_file)
        with open(test_file, "r") as f:
            assert f.read() == "TeSt StRiNg\n"


@pytest.mark.parametrize("create_package", [util.get_library_package_path()], indirect=True)
def test_simple(create_package, capsys):
    """
    Test exporting to dlazaw debian package.
    """
    package_path = create_package
    parser = configure_parsers()
    args = parser.parse_args(['export', '--ocen'])
    command = Command()
    command.run(args)

    out = capsys.readouterr().out
    _test_deb(os.path.join(package_path, "export"), out)


@pytest.mark.parametrize("create_package", [util.get_library_package_path()], indirect=True)
def test_output_flag(create_package, capsys):
    """
    Test exporting to dlazaw debian package with --output flag.
    """
    with tempfile.TemporaryDirectory() as output_dir:
        parser = configure_parsers()
        args = parser.parse_args(['export', '--ocen', '--output', output_dir])
        command = Command()
        command.run(args)

        out = capsys.readouterr().out
        _test_deb(output_dir, out)
