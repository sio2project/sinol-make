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


class Sio2JailException(SinolMakeException):
    def __init__(self, return_code, jail_stderr):
        self.return_code = return_code
        self.jail_stderr = jail_stderr

    def __str__(self):
        return f"sio2jail failed with exit code {self.return_code}:\n{self.jail_stderr}"
