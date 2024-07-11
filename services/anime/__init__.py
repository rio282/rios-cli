from typing import Final

from anipy_api.provider import get_provider

from .downloader_service import Downloader
from .lookup_service import Search

ANIME_PROVIDER: Final[str] = "gogoanime"

provider = get_provider(ANIME_PROVIDER)
lookup = Search(provider)
downloader = Downloader()
