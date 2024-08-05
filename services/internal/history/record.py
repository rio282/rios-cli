from datetime import datetime
from typing import List, Final


class Record:
    def __init__(self, timestamp: datetime, command: str, subcommands: List[str]):
        self.timestamp: Final[datetime] = timestamp
        self.command: Final[str] = command
        self.subcommands: Final[List[str]] = subcommands

    def __repr__(self):
        return f"{int(self.timestamp.timestamp())} -> {self.command}, <{' '.join(self.subcommands)}>"
