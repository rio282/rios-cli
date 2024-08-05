import os
from typing import Final

from .osys import COMService, ProcessManager, StatisticsService
from .osys.fs import FileSystem
from .search.web import DuckDuckGo, WebSearcher
from .search.local import LocalSearcher
from .internal.history import HistoryManager

cache_directory: Final[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, ".cache")
if not os.path.exists(cache_directory):
    os.mkdir(cache_directory)

file_system = FileSystem(cache_directory)
processes = ProcessManager()
statistics = StatisticsService()
com = COMService()
local_searcher = LocalSearcher()
web_searcher = DuckDuckGo(query_url=f"https://duckduckgo.com/html/?q={WebSearcher.QUERY_PLACEHOLDER}",
                          cache_dir=cache_directory)
history_manager = HistoryManager(cache_directory)
