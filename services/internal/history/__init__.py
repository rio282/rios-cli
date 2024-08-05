import os
import pickle
from datetime import datetime as dt
from typing import List, Final

from .record import Record


class HistoryManager:
    def __init__(self, cache_dir):
        self.cache_dir: Final[str] = cache_dir
        self.cache_file: Final[str] = f"{cache_dir}/cmd.history"
        self.history: List[Record] = []

    def record_line(self, line) -> None:
        line = line.split()
        command = line[0]
        subcommands = line[1:] if len(line) > 1 else []

        self.history.append(Record(dt.now(), command, subcommands))

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
