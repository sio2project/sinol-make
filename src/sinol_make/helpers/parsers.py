from sinol_make.compilers.CompilersManager import CompilerManager


def add_compilation_arguments(parser):
    CompilerManager.add_args(parser)
