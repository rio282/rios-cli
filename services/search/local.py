import os
import fnmatch

from typing import List
from fuzzywuzzy import fuzz
from concurrent.futures import ThreadPoolExecutor, as_completed


class LocalSearchResult:
    def __init__(self, title: str, location: str, ranking: int = -1):
        self.title = title
        self.location = location
        self.ranking = ranking

    def __repr__(self):
        return f"{self.title} - {self.location}"


class LocalSearcher:
    def __init__(self, search_threshold: int = 50):
        self.search_threshold = search_threshold

    def search(self, directories: List[str], fn_query: str, file_types: str = "") -> List[LocalSearchResult]:
        matches = []

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.__search_directory, directory, fn_query, file_types):
                    directory for directory in directories
            }
            for future in as_completed(futures):
                matches.extend(future.result())

        return matches

    def __search_directory(self, directory: str, query: str, file_types: str) -> List[LocalSearchResult]:
        matches = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(tuple(ft for ft in file_types)) or file_types[0] == "":
                    if fuzz.token_sort_ratio(query.lower(), filename.lower()) > self.search_threshold or query == "":
                        match = LocalSearchResult(filename, os.path.join(root, filename))
                        matches.append(match)
        return matches
