from dataclasses import dataclass

from sinol_make.programs.solution import Solution
from sinol_make.tests.input import InputTest
from sinol_make.tests.output import OutputTest


@dataclass
class OutputGenerationArguments:
    """
    Arguments used for function that generates output file.
    """
    # Path to correct solution executable
    correct_solution: Solution
    # Path to input file
    input_test: InputTest
    # Path to output file
    output_test: OutputTest
