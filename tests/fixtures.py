import pytest, tempfile, os, shutil
from .util import get_simple_package_path

@pytest.fixture
def create_package():
    tmpdir = tempfile.TemporaryDirectory()
    package_path = os.path.join(tmpdir.name, "abc")
    shutil.copytree(get_simple_package_path(), package_path)
    os.chdir(package_path)

    yield package_path

    tmpdir.cleanup()
