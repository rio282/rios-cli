from abc import abstractmethod, ABC, ABCMeta
from typing import List, Final, Dict

import requests
from bs4 import BeautifulSoup

from . import SearchResult, Searcher


class WebSearcher(Searcher, metaclass=ABCMeta):
    QUERY_PLACEHOLDER: Final[str] = "<SEARCH_QUERY>"

    def __init__(self, cache_dir: str, query_url: str, authority: str = "WEB"):
        super().__init__(cache_dir, "search", authority=authority)
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


class DuckDuckGoSearcher(WebSearcher, metaclass=ABCMeta):
    def __init__(self, cache_dir: str, query_url: str):
        super().__init__(cache_dir, query_url, authority="DDG")

    def search(self, query: str) -> List[SearchResult]:
        # check if data is available in cache
        if query in self.results_cache:
            return self.results_cache[query]

        # construct queried url
        search_url = self.querify(query)

        # do request
        response = requests.get(search_url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Error: Unable to retrieve search results (status code: {response.status_code})")

        # parse web data
        soup = BeautifulSoup(response.text, "html.parser")
        web_results = soup.find_all("a", class_="result__a")

        search_results = []
        for index, result in enumerate(web_results, start=1):
            title = result.get_text()
            href = result.get("href")
            search_result = SearchResult(title, href, ranking=index)
            search_results.append(search_result)

        # save results to cache & return
        self.results_cache[query] = search_results
        return search_results
