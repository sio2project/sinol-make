import pytest, tempfile, os, shutil
from .util import get_simple_package_path


@pytest.fixture
def create_package(request):
    """
    Fixture to create a temporary directory with specified package (by default simple package).
    Changes the current working directory to the package directory.
    """
    try:
        path = request.param
    except AttributeError:
        path = get_simple_package_path()
    task_id = os.path.basename(path)

    tmpdir = tempfile.TemporaryDirectory()
    package_path = os.path.join(tmpdir.name, task_id)
    shutil.copytree(path, package_path)
    os.chdir(package_path)

    yield package_path

    tmpdir.cleanup()


@pytest.fixture
def temp_workdir():
    """
    Fixture to change the current working directory to the temporary directory.
    """
    tmpdir = tempfile.TemporaryDirectory()
    print(tmpdir)
    os.chdir(tmpdir.name)
    
    yield tmpdir.name
    
    tmpdir.cleanup()
