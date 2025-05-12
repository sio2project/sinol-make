import os

from sio3pack import Package
from sio3pack import LocalFile


def _get_local_file():
    return LocalFile(os.getcwd())


class SIO3Package:
    """
    Singleton class for package base class.
    """

    _instance = None

    def __new__(cls) -> Package:
        if cls._instance is None:
            cls._instance = Package.from_file(_get_local_file())
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None
