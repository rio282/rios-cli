from abc import abstractmethod, ABC
from typing import List, Final, Optional, Dict

import requests
from bs4 import BeautifulSoup


class SearchResult:
    def __init__(self, title: str, href: str, ranking: int = -1):
        self.title = title
        self.href = href
        self.ranking = ranking

    def __repr__(self):
        return f"{self.title} - {self.href}"


class WebSearcher(ABC):
    QUERY_PLACEHOLDER: Final[str] = "<SEARCH_QUERY>"

    def __init__(self, query_url: str):
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


class DuckDuckGo(WebSearcher, ABC):
    def __init__(self, query_url: str):
        super().__init__(query_url)

    def search(self, query: str) -> List[SearchResult]:
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

        return search_results
