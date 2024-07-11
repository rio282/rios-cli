from typing import List

from anipy_api.anime import Anime
from anipy_api.provider import BaseProvider, LanguageTypeEnum, Episode


class Search:
    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def search_anime_by_name(self, anime_name: str) -> List[Anime]:
        anime = []

        results = self.provider.get_search(anime_name)
        for r in results:
            anime.append(Anime.from_search_result(self.provider, r))

        return anime

    def get_episodes_by_anime(self, anime: Anime, lang=LanguageTypeEnum.SUB) -> List[Episode]:
        return anime.get_episodes(lang=lang)
