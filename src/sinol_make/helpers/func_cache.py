import os

__cache = {}


def cache_result(cwd=False):
    """
    Function to cache the result of a function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if cwd:
                key = (func.__name__, os.getcwd())
            else:
                key = func.__name__

            if key in __cache:
                return __cache[key]
            result = func(*args, **kwargs)
            __cache[key] = result
            return result
        return wrapper
    return decorator


def clear_cache():
    """
    Function to clear the cache.
    """
    __cache.clear()
