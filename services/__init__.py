import os
from typing import Final

from .osys import COMService, ProcessManager
from .osys.fs import FileSystem
from .osys.info import SysInfo
from .search.web import DuckDuckGoSearcher, WebSearcher
from .search.local import LocalSearcher
from .internal.history import HistoryManager

cache_directory: Final[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, ".cache")
if not os.path.exists(cache_directory):
    os.mkdir(cache_directory)

file_system = FileSystem(cache_directory)
processes = ProcessManager()
sysinfo = SysInfo()
com = COMService()
local_searcher = LocalSearcher(cache_dir=cache_directory)
web_searcher = DuckDuckGoSearcher(cache_dir=cache_directory,
                                  query_url=f"https://duckduckgo.com/html/?q={WebSearcher.QUERY_PLACEHOLDER}")
history_manager = HistoryManager(cache_directory)
