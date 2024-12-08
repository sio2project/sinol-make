import os
import tempfile

from sinol_make.commands.init import Command


def test_if_download_successful():
    command = Command()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_dir = command.download_template(tmpdir)
        assert os.path.isfile(os.path.join(tmp_dir,'config.yml'))
