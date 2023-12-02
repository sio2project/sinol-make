from sinol_make import util
from sinol_make.timetools.sio2jail import Sio2jailTimeTool


class Sio2jailRealTimeTool(Sio2jailTimeTool):
    def get_name(self) -> str:
        return "time"

    def is_available(self) -> bool:
        return self.is_latest_version()

    def get_priority(self) -> int:
        return 1

    def _use_real_time(self) -> bool:
        return True
