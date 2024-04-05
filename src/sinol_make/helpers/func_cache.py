__cache = {}


def cache_result(func):
    """
    Function to cache the result of a function.
    """
    def wrapper(*args, **kwargs):
        if func.__name__ in __cache:
            return __cache[func.__name__]
        result = func(*args, **kwargs)
        __cache[func.__name__] = result
        return result
    return wrapper
