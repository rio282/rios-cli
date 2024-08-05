class SearchResult:
    def __init__(self, title: str, location: str, ranking: int = -1):
        self.title = title
        self.location = location
        self.ranking = ranking

    def __repr__(self):
        return f"{self.title} - {self.location}"
