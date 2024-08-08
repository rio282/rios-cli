import os.path
import pickle
import time
from datetime import timedelta
from typing import List, Dict, Tuple, Final

from anipy_api.anime import Anime
from anipy_api.provider import BaseProvider, LanguageTypeEnum, Episode


class Search:
    CACHE_EXPIRATION_TIME: Final[timedelta] = timedelta(hours=12)

    def __init__(self, cache_dir: str, provider: BaseProvider):
        self.cache_file = os.path.join(cache_dir, "anime.cache")
        self.provider = provider
        self.animes_cache: Dict[str, Tuple[float, List[Anime]]] = {}

    def search_anime_by_name(self, anime_name: str, force_refresh: bool = False) -> List[Anime]:
        """
        Search for anime by name, utilizing cache to avoid redundant searches if the cache is not expired.

        :param anime_name: The name of the anime to search for.
        :param force_refresh: Forces search to refresh, even when the results are already stored in cache.
        :return: A list of Anime objects that match the search criteria.
        """
        current_time = time.time()

        # no point in checking the cache if we need to force refresh
        if not force_refresh and anime_name in self.animes_cache:
            cache_time, cached_anime = self.animes_cache[anime_name]
            if current_time - cache_time < self.CACHE_EXPIRATION_TIME.total_seconds():
                return cached_anime

        # perform search if not in cache or cache expired
        results = self.provider.get_search(anime_name)
        animes = [Anime.from_search_result(self.provider, r) for r in results]

        self.animes_cache[anime_name] = (current_time, animes)
        return animes

    def get_episodes_by_anime(self, anime: Anime, lang: LanguageTypeEnum = LanguageTypeEnum.SUB) -> List[Episode]:
        """
        Get a list of episodes for a given anime in the specified language.

        :param anime: The Anime object for which to fetch episodes.
        :param lang: The language type for the episodes (default is LanguageTypeEnum.SUB).
        :return: A list of Episode objects.
        """
        return anime.get_episodes(lang=lang)

    def save(self) -> None:
        """
        Saves the cache to a file.
        """
        try:
            with open(file=self.cache_file, mode="wb") as f:
                pickle.dump({"animes_cache": self.animes_cache}, f)
        except Exception as e:
            print("Couldn't save cache.")
            print(e)

    def load(self) -> None:
        """
        Loads the cache from a file.
        """
        if os.path.exists(self.cache_file):
            with open(file=self.cache_file, mode="rb") as f:
                cache_data = pickle.load(f)
                self.animes_cache = cache_data.get("animes_cache", {})
