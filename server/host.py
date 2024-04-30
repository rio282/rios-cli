class Host:
    def __init__(self, port: int, max_clients: int = 1):
        self.port = port
        self.max_clients = max_clients

    def run(self) -> None:
        pass
