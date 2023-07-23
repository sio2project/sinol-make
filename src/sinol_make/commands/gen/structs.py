from dataclasses import dataclass


@dataclass
class OutputGenerationArguments:
    """
    Arguments used for function that generates output file.
    """
    correct_solution_exe: str
    input_test: str
    output_test: str
