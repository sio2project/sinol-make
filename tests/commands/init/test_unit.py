import os
import tempfile
import pytest

from sinol_make.commands.init import Command


def copy_template(rootdir):
    template_path = [rootdir, Command.DEFAULT_SUBDIR]
    command = Command()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = command.download_template(tmpdir, template_path)
        assert os.path.isfile(os.path.join(tmp_dir, 'config.yml'))


def test_clones_default_template(request):
    # try to avoid connecting to github when cloning example_package
    rootdir = str(request.config.rootdir)
    git_dir = os.path.join(rootdir, '.git')
    if not os.path.exists(git_dir):
        # if needed we could take a dependency on gitpython and mock up a repo
        pytest.skip(f".git not found in rootdir {rootdir}")

    git_local_url = os.path.join('file://', rootdir)
    copy_template(git_local_url)


def test_copies_local_template_absolute_path(request):
    rootdir_absolute = str(request.config.rootdir)
    copy_template(rootdir_absolute)


def test_copies_local_template_relative_path(request):
    os.chdir(os.path.join(request.config.rootdir, '..'))
    rootdir_relative = os.path.relpath(request.config.rootdir, os.getcwd())
    copy_template(rootdir_relative)
