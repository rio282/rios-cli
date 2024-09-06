import time
import sys
from typing import IO


class Server:
    def __init__(self, stdout: IO = sys.stdout):
        self.stdout: IO = stdout
        self.running: bool = False

    def log(self, message: str) -> None:
        print(str(message), file=self.stdout, flush=True)

    def start(self) -> None:
        self.running = True
        while self.running:
            self.log("Server is running...")
            time.sleep(1)

    def stop(self) -> None:
        self.running = False
