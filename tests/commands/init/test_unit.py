import os

from sinol_make.commands.init import Command


def test_if_download_successful():
    command = Command()
    tmp_dir = command.download_template()
    assert os.path.isfile(os.path.join(tmp_dir,'config.yml'))
