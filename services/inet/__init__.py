import subprocess


class Server:
    def __init__(self, stdout=subprocess.STDOUT):
        self.stdout = stdout
        self.running = False

    def start(self) -> None:
        self.running = True
        while self.running:
            pass

    def stop(self) -> None:
        self.running = False
