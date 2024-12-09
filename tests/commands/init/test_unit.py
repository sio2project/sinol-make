import os
import tempfile

from sinol_make.commands.init import Command


def copy_template(rootdir):
    template_path = [rootdir, Command.DEFAULT_SUBDIR]
    command = Command()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = command.download_template(tmpdir, template_path)
        assert os.path.isfile(os.path.join(tmp_dir, 'config.yml'))


def test_clones_default_template(request):
    # try to avoid connecting to github when cloning example_package
    git_dir = os.path.join(request.config.rootdir, '.git')
    if os.path.exists(git_dir):
        git_local_url = os.path.join('file://', request.config.rootdir)
        copy_template(git_local_url)
    else:
        # currently this does fallback on github if the local repo is not available
        # if needed we could take a dependency on gitpython and mock up a repo
        copy_template(Command.DEFAULT_TEMPLATE)


def test_copies_local_template_absolute_path(request):
    rootdir_absolute = str(request.config.rootdir)
    copy_template(rootdir_absolute)


def test_copies_local_template_relative_path(request):
    os.chdir(os.path.join(request.config.rootdir, '..'))
    rootdir_relative = os.path.relpath(request.config.rootdir, os.getcwd())
    copy_template(rootdir_relative)
