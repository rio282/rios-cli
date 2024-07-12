import os.path
from pathlib import Path
from typing import Final

from anipy_api.anime import Anime
from anipy_api.download import Downloader as AniPyDownloader
from anipy_api.provider import LanguageTypeEnum

from etc import escape_windows_safe_filename
from etc.loading_screen import Loader


class Downloader:
    class Quality:
        QUALITY_BEST: Final[str] = "best"
        QUALITY_WORST: Final[str] = "worst"
        QUALITY_1080P: Final[int] = 1080
        QUALITY_720P: Final[int] = 720

    def __init__(self):
        self.loader = Loader("Downloading...")
        self.animes_folder = os.path.join(os.path.expanduser("~/Videos"), "anime")

    def download_episode(self, anime: Anime, episode_number: int, language: LanguageTypeEnum = LanguageTypeEnum.SUB,
                         preferred_quality: str = Quality.QUALITY_720P) -> Path:
        try:
            # prepare stream
            stream = anime.get_video(episode_number, lang=language, preferred_quality=preferred_quality)

            # prepare download path
            download_path = Path(self.animes_folder, escape_windows_safe_filename(anime.get_info().name))
            download_path.mkdir(parents=True, exist_ok=True)

            # download
            downloader = AniPyDownloader(self.__progress_callback, self.__info_callback)
            return downloader.download(
                stream=stream,
                download_path=download_path,
                container=".mkv",
                ffmpeg=False
            )
        except:
            raise

    def __info_callback(self, message: str):
        pass

    def __progress_callback(self, percentage: float):
        self.loader.update_loader(percentage)
