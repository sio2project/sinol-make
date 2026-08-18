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
