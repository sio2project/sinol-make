__verbose__ = False


def set_verbose(verbose: bool):
    global __verbose__
    __verbose__ = verbose


def is_verbose() -> bool:
    return __verbose__


def debug(message: str):
    if is_verbose():
        print(message)
