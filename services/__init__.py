import os

from .osys.file_service import FileSystem
from .osys.network_service import Network

f_file_cache = os.path.join(os.getcwd(), "ls.cache")
file_system = FileSystem(f_file_cache)

network = Network()
