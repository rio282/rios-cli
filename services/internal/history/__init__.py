import os
import pickle
from datetime import datetime
from typing import List, Final


class Record:
    def __init__(self, timestamp: datetime, command: str, subcommands: List[str]):
        self.timestamp: Final[datetime] = timestamp
        self.command: Final[str] = command
        self.subcommands: Final[List[str]] = subcommands

    def __repr__(self):
        return f"{self.timestamp} @ {self.command.center(32)} & [{' '.join(self.subcommands)}]"


class HistoryManager:
    def __init__(self, cache_dir: str):
        self.cache_dir: Final[str] = cache_dir
        self.cache_file: Final[str] = f"{cache_dir}/cmd.history"
        self.history: List[Record] = []

    def record_line(self, line: str) -> None:
        if not line.strip():  # empty line
            return

        parts = line.split()
        command = parts[0]
        subcommands = parts[1:]

        self.history.append(Record(datetime.now(), command, subcommands))

    def save(self) -> bool:
        try:
            with open(file=self.cache_file, mode="wb") as f:
                pickle.dump({"history": self.history}, f)
        except Exception as e:
            return False
        return True

    def load(self) -> bool:
        if os.path.exists(self.cache_file):
            with open(file=self.cache_file, mode="rb") as f:
                cache_data = pickle.load(f)
                self.history = cache_data.get("history", {})
            return True
        return False
