class SinolMakeException(Exception):
    pass


class CompilationError(SinolMakeException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class CheckerException(SinolMakeException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class UnknownContestType(SinolMakeException):
    pass
