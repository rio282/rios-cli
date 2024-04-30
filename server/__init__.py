import socket

from typing import Final

import requests

from .host import Host
from .client import Client


def get_public_ipv4() -> str:
    try:
        response = requests.get("https://api.ipify.org")
        if response.status_code == 200:
            return response.text
        else:
            raise Exception("Failed to retrieve public IPv4 address.")
    except Exception:
        return "UNKNOWN"


LOCALHOST: Final[str] = "127.0.0.1"
COMMON_PORT: Final[int] = 55555
ADDRESS_PRIVATE: Final[str] = socket.gethostbyname(socket.gethostname())
ADDRESS_PUBLIC: Final[str] = get_public_ipv4()
MAX_CLIENTS: Final[int] = 5

host: Final[Host] = Host(port=COMMON_PORT, max_clients=MAX_CLIENTS)
client: Final[Client] = Client(port=COMMON_PORT)
