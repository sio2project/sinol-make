import os


def get_cache_path():
    """
    Function to get the path to the cache directory.
    """
    return os.path.join(os.getcwd(), ".cache")


def get_path_in_cache(*paths):
    """
    Function to get a path in the cache directory. Works the same as os.path.join.
    """
    return os.path.join(get_cache_path(), *paths)


def get_executables_path():
    """
    Function to get the path to the executables directory inside of cache.
    """
    return get_path_in_cache("executables")


def get_path_in_executables(*paths):
    """
    Function to get a path in executables directory. Works the same as os.path.join.
    """
    return os.path.join(get_executables_path(), *paths)


def get_compilation_log_path():
    """
    Function to get the path to the compilation log directory inside of cache.
    """
    return get_path_in_cache("compilation")


def get_path_in_compilation_log(*paths):
    """
    Function to get a path in compilation log directory. Works the same as os.path.join.
    """
    return os.path.join(get_compilation_log_path(), *paths)


def get_executions_path():
    """
    Function to get the path to the executions directory inside of cache.
    """
    return get_path_in_cache("executions")


def get_path_in_executions(*paths):
    """
    Function to get a path in executions directory. Works the same as os.path.join.
    """
    return os.path.join(get_executions_path(), *paths)
