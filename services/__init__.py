import os

from .osys import COMService, ProcessManager
from .osys.file_service import FileSystem
from .osys.network_service import NetworkService

f_file_cache = os.path.join(os.getcwd(), "ls.cache")
file_system = FileSystem(f_file_cache)

network = NetworkService()
processes = ProcessManager()
com = COMService()
