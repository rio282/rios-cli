import os

from typing import List
import concurrent.futures


class LocalSearchResult:
    def __init__(self, title: str, location: str, ranking: int = -1):
        self.title = title
        self.location = location
        self.ranking = ranking

    def __repr__(self):
        return f"{self.title} - {self.location}"


class LocalSearcher:
    def __init__(self):
        super().__init__()

    def search(self, query: str) -> List[LocalSearchResult]:
        matches = []
        ranking = 1

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.__search_directory, root, query) for root in self.__get_search_roots()]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                for match in result:
                    match.ranking = ranking
                    ranking += 1
                matches.extend(result)

        return matches

    def __get_search_roots(self):
        # Adjust the search roots as needed
        return ["/"]

    def __search_directory(self, directory, query):
        matches = []
        for root, dirs, files in os.walk(directory):
            for name in files:
                if query.lower() in name.lower():
                    matches.append(LocalSearchResult(title=name, location=os.path.join(root, name)))
            for name in dirs:
                if query.lower() in name.lower():
                    matches.append(LocalSearchResult(title=name, location=os.path.join(root, name)))
        return matches
