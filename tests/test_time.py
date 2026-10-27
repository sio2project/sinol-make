import pytest

from sinol_make.executors import time as time_executor


@pytest.mark.parametrize("platform, time_name", [("linux", "time"), ("darwin", "gtime")])
def test_missing_time(monkeypatch, tmp_path, capsys, platform, time_name):
    monkeypatch.setattr(time_executor.sys, "platform", platform)
    monkeypatch.setenv("PATH", str(tmp_path))

    with pytest.raises(SystemExit) as exc:
        time_executor.TimeExecutor()

    assert exc.value.code == 1
    assert f"{time_name} not found" in capsys.readouterr().out


@pytest.mark.parametrize("platform, time_name", [("linux", "time"), ("darwin", "gtime")])
def test_time_path(monkeypatch, tmp_path, platform, time_name):
    monkeypatch.setattr(time_executor.sys, "platform", platform)
    time_dir = tmp_path / "time tools"
    time_dir.mkdir()
    time_path = time_dir / time_name
    time_path.write_text("#!/bin/sh\nexit 0\n")
    time_path.chmod(0o755)
    monkeypatch.setenv("PATH", str(time_dir))

    executor = time_executor.TimeExecutor()
    command = executor._wrap_command(["./solution"], "/tmp/result", 1000, 262144)

    assert command[0] == f'"{time_path}"'
