import os
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Final, Dict

from fuzzywuzzy import fuzz

from . import SearchResult


class LocalSearcher:
    def __init__(self, cache_dir: str, search_threshold: int = 50):
        self.cache_dir: Final[str] = cache_dir
        self.cache_file: Final[str] = f"{cache_dir}/slocal.cache"
        self.search_threshold: int = search_threshold
        self.results_cache: Dict[str, List[SearchResult]] = {}

    def search(self, directories: List[str], fn_query: str, file_types: str = "") -> List[SearchResult]:
        matches = []

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.__search_directory, directory, fn_query, file_types):
                    directory for directory in directories
            }
            for future in as_completed(futures):
                matches.extend(future.result())

        return matches

    def __search_directory(self, directory: str, query: str, file_types: str) -> List[SearchResult]:
        matches = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(tuple(ft for ft in file_types)) or file_types[0] == "":
                    if fuzz.token_sort_ratio(query.lower(), filename.lower()) > self.search_threshold or query == "":
                        match = SearchResult(filename, os.path.join(root, filename))
                        matches.append(match)
        return matches

    def save_cache(self) -> None:
        # TODO: move to Searcher class in init file
        """
        Saves the cache to a file.
        """
        try:
            with open(file=self.cache_file, mode="wb") as f:
                pickle.dump({"results_cache": self.results_cache}, f)
        except Exception as e:
            print("Couldn't save cache.")
            print(e)

    def load_cache(self) -> None:
        """
        Loads the cache from a file.
        """
        if os.path.exists(self.cache_file):
            with open(file=self.cache_file, mode="rb") as f:
                cache_data = pickle.load(f)
                self.results_cache = cache_data.get("results_cache", {})
