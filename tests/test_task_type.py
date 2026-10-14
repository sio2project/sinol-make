import os
import pytest

from sinol_make.helpers import oicompare
from sinol_make.task_type import BaseTaskType
from sinol_make.task_type.normal import NormalTaskType


@pytest.mark.skipif(not oicompare.check_installed(), reason="oicompare is not installed")
def test_oicompare_arguments_order(tmpdir):
    """
    Tests if the contestant's output and the correct answer are passed to oicompare in the right order.
    """
    output_file = os.path.join(tmpdir, "out.out")
    answer_file = os.path.join(tmpdir, "ans.out")
    with open(output_file, "w") as f:
        f.write("contestant\n")
    with open(answer_file, "w") as f:
        f.write("correct\n")

    # __init__ requires a package, which isn't needed for running oicompare.
    task_type = BaseTaskType.__new__(NormalTaskType)
    correct, points, comment, _ = task_type._run_oicompare(output_file, answer_file)
    assert not correct
    assert points == 0
    assert 'expected "correct"' in comment
    assert 'got "contestant"' in comment

    with open(output_file, "w") as f:
        f.write("correct\n")
    correct, points, comment, _ = task_type._run_oicompare(output_file, answer_file)
    assert correct
    assert points == 100
    assert comment == ""


@pytest.mark.parametrize("exit_code", [3, 4])
def test_checker_failing_exit_code(tmpdir, exit_code):
    """
    Tests if a checker exiting with code greater than 2 is reported as a wrong answer
    instead of crashing on unpacking the result.
    """
    checker_path = os.path.join(tmpdir, "chk.e")
    with open(checker_path, "w") as f:
        f.write(f"#!/bin/sh\necho 'checker failure' >&2\nexit {exit_code}\n")
    os.chmod(checker_path, 0o755)
    files = []
    for name in ["in.in", "out.out", "ans.out"]:
        files.append(os.path.join(tmpdir, name))
        with open(files[-1], "w") as f:
            f.write("1\n")

    task_type = BaseTaskType.__new__(NormalTaskType)
    task_type.has_checker = True
    task_type.checker_path = checker_path
    correct, points, comment, stderr = task_type.check_output(*files)
    assert not correct
    assert points == 0
    assert f"Checker returned with code {exit_code}" in comment
    assert "checker failure" in stderr
