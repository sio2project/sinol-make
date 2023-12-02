from sinol_make.commands.gen import gen_util, Command
from sinol_make.structs.gen_structs import OutputGenerationArguments
from sinol_make.helpers import package_util
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest
from tests import util
from tests.fixtures import *


@pytest.mark.parametrize("create_package", [util.get_simple_package_path()], indirect=True)
def test_generate_output(create_package):
    """
    Test generating outputs.
    """
    task_id = package_util.get_task_id()
    command: Command = util.get_gen_command()
    command.base_run(None)
    ingen = command.get_ingen()
    exe, _ = ingen.compile()
    assert exe is not None
    solution = command.get_solution()
    exe, _ = solution.compile()
    assert exe is not None
    ingen.run()
    input = InputTest(task_id, "in/abc1a.in")
    output = OutputTest(task_id, "out/abc1a.out", exists=False)
    assert gen_util.generate_output(OutputGenerationArguments(
        correct_solution=solution,
        input_test=input,
        output_test=output
    ))
    assert output.exists()
