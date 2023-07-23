from dataclasses import dataclass


@dataclass
class OutputGenerationArguments:
    """
    Arguments used for function that generates output file.
    """
    # Path to correct solution executable
    correct_solution_exe: str
    # Path to input file
    input_test: str
    # Path to output file
    output_test: str
