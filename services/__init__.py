import os

from .osys import COMService, ProcessManager, StatisticsService
from .osys.fs import FileSystem
from .osys.net import NetworkService
from .search import DuckDuckGo, WebSearcher

f_file_cache = os.path.join(os.getcwd(), "ls.cache")
file_system = FileSystem(f_file_cache)

network = NetworkService()
processes = ProcessManager()
statistics = StatisticsService()
com = COMService()
web_searcher = DuckDuckGo(query_url=f"https://duckduckgo.com/html/?q={WebSearcher.QUERY_PLACEHOLDER}")
