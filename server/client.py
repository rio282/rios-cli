class Client:
    def __init__(self, port: int):
        self.port = port
        self.server_address = "<NOT_SET>"

    def prompt_server_address(self) -> None:
        self.server_address = input("Server address: ")

    def run(self) -> None:
        pass
