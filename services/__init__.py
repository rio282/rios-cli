import os

from .osys.file_service import FileSystem

cache_file = os.path.join(os.getcwd(), "ls.cache")
file_system = FileSystem(cache_file)
file_system.load_cache()
