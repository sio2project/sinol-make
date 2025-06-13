import os

from sio3pack.packages.sinolpack import Sinolpack
from sio3pack.packages.package import Package
from sio3pack.files import LocalFile


def _get_local_file():
    return LocalFile(os.getcwd())


class SIO3Package:
    """
    Singleton class for package base class.
    """

    _instance = None

    def __new__(cls) -> Sinolpack:
        if cls._instance is None:
            cls._instance = Package.from_file(_get_local_file())
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None
