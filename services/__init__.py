import os

from .osys.com_service import COMService
from .osys.file_service import FileSystem
from .osys.network_service import NetworkService

f_file_cache = os.path.join(os.getcwd(), "ls.cache")
file_system = FileSystem(f_file_cache)

network = NetworkService()

com = COMService()
