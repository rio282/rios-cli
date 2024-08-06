import os
from abc import ABCMeta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from fuzzywuzzy import fuzz

from . import SearchResult, Searcher


class LocalSearcher(Searcher, metaclass=ABCMeta):
    def __init__(self, cache_dir: str):
        super().__init__(cache_dir, "search", authority="LOCAL")

    def search(self, directories: List[str], fn_query: str, file_types: str = "", search_threshold: int = 50) -> \
            List[SearchResult]:
        matches = []

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.__search_directory, directory, fn_query, file_types, search_threshold):
                    directory for directory in directories
            }
            for future in as_completed(futures):
                matches.extend(future.result())

        return matches

    def __search_directory(self, directory: str, query: str, file_types: str, search_threshold: int) -> \
            List[SearchResult]:
        matches = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(tuple(ft for ft in file_types)) or file_types[0] == "":
                    if fuzz.token_sort_ratio(query.lower(), filename.lower()) > search_threshold or query == "":
                        match = SearchResult(filename, os.path.join(root, filename))
                        matches.append(match)
        return matches
