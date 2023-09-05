import os


def get_cache_path(*paths):
    """
    Function to get a path in the cache directory. Works the same as os.path.join.
    With no arguments, it returns the path to the cache directory.
    """
    return os.path.join(os.getcwd(), ".cache", *paths)


def get_executables_path(*paths):
    """
    Function to get a path in executables directory. Works the same as os.path.join.
    With no arguments, it returns the path to the executables directory.
    """
    return os.path.join(get_cache_path("executables"), *paths)


def get_compilation_log_path(*paths):
    """
    Function to get a path in compilation log directory. Works the same as os.path.join.
    With no arguments, it returns the path to the compilation log directory.
    """
    return os.path.join(get_cache_path("compilation"), *paths)


def get_executions_path(*paths):
    """
    Function to get a path in executions directory. Works the same as os.path.join.
    With no arguments, it returns the path to the executions directory.
    """
    return os.path.join(get_cache_path("executions"), *paths)
