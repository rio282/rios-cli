import os
import pickle
from abc import abstractmethod, ABC
from typing import List, Final, Dict

import requests
from bs4 import BeautifulSoup

from . import SearchResult


class WebSearcher(ABC):
    QUERY_PLACEHOLDER: Final[str] = "<SEARCH_QUERY>"

    def __init__(self, query_url: str, cache_dir: str):
        self.cache_file: Final[str] = f"{cache_dir}/sweb.cache"
        self.results_cache: Dict[str, List[SearchResult]] = {}

        self.headers: Final[Dict[str, str]] = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.query_url: Final[str] = query_url

    @abstractmethod
    def search(self, query: str) -> List[SearchResult]:
        pass

    def querify(self, search_query: str) -> str:
        search_query = search_query.strip().replace(" ", "+")
        query_url = self.query_url.replace(self.QUERY_PLACEHOLDER, search_query)
        return query_url

    def save_cache(self) -> None:
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
        # TODO: move to Searcher class in init file
        """
        Loads the cache from a file.
        """
        if os.path.exists(self.cache_file):
            with open(file=self.cache_file, mode="rb") as f:
                cache_data = pickle.load(f)
                self.results_cache = cache_data.get("results_cache", {})


class DuckDuckGo(WebSearcher, ABC):
    def __init__(self, query_url: str, cache_dir: str):
        super().__init__(query_url, cache_dir)

    def search(self, query: str) -> List[SearchResult]:
        if query in self.results_cache:
            return self.results_cache[query]

        search_url = self.querify(query)

        response = requests.get(search_url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Error: Unable to retrieve search results (status code: {response.status_code})")

        soup = BeautifulSoup(response.text, "html.parser")
        web_results = soup.find_all("a", class_="result__a")

        search_results = []
        for index, result in enumerate(web_results, start=1):
            title = result.get_text()
            href = result.get("href")
            search_result = SearchResult(title, href, ranking=index)
            search_results.append(search_result)

        self.results_cache[query] = search_results
        return search_results
