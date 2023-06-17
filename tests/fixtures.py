import pytest, tempfile, os, shutil
from .util import get_simple_package_path


@pytest.fixture
def create_package(path=None):
    if path is None:
        path = get_simple_package_path()
    tmpdir = tempfile.TemporaryDirectory()
    package_path = os.path.join(tmpdir.name, "abc")
    shutil.copytree(path, package_path)
    os.chdir(package_path)

    yield package_path

    tmpdir.cleanup()
