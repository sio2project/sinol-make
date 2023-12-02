from sinol_make.programs.solution import Solution
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest


def generate_output(arguments):
    """
    Generates output file for given input file.
    :param arguments: arguments for output generation (type OutputGenerationArguments)
    :return: True if the output was successfully generated, False otherwise
    """
    input_test: InputTest = arguments.input_test
    output_test: OutputTest = arguments.output_test
    correct_solution: Solution = arguments.correct_solution

    with input_test.open('r') as input_file, output_test.open('w') as output_file:
        exit_code = correct_solution.run(stdin=input_file, stdout=output_file)

    return exit_code == 0
