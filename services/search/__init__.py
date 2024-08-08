import json

import xxhash
import os
import pickle
from abc import ABC, ABCMeta
from typing import Final, Dict, List, Optional


class Searcher(ABC, metaclass=ABCMeta):
    def __init__(self, cache_dir: str, cache_fn: str, authority: str = "DEFAULT"):
        self.cache_dir: Final[str] = cache_dir
        self.cache_file: Final[str] = f"{cache_dir}/{cache_fn}.cache"
        self.results_cache: Dict[str, List[SearchResult]] = {}
        self.hash_name: Final[str] = xxhash.xxh64(authority).hexdigest()

    def save(self) -> bool:
        """
        Saves the cache to a file.
        """
        try:
            # read existing contents
            try:
                with open(file=self.cache_file, mode="rb") as f:
                    full_cache = pickle.load(f)
            except (FileNotFoundError, EOFError):
                full_cache = {}
            full_cache[self.hash_name] = self.results_cache

            # write full cache into file
            with open(file=self.cache_file, mode="wb") as f:
                pickle.dump(full_cache, f)
        except Exception as e:
            # bad...
            print("Couldn't save cache.")
            print(e)
            return False
        return True

    def load(self) -> Optional[Dict[str, List["SearchResult"]]]:
        """
        Loads the cache from a file.
        """
        if os.path.exists(self.cache_file):
            with open(file=self.cache_file, mode="rb") as f:
                cache_data = pickle.load(f)
                self.results_cache = cache_data.get(self.hash_name, {})
            return self.results_cache
        return {}


class SearchResult:
    def __init__(self, title: str, location: str, ranking: int = -1):
        self.title: str = title
        self.location: str = location
        self.ranking: int = ranking

    def __repr__(self):
        return f"{self.title} - {self.location}"
