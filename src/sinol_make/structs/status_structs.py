from enum import Enum


class Status(str, Enum):
    NO_STATUS = "  "
    CE = "CE"
    TL = "TL"
    ML = "ML"
    RE = "RE"
    WA = "WA"
    OK = "OK"

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
