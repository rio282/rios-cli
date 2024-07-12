import os.path
from pathlib import Path
from typing import Final

from anipy_api.anime import Anime
from anipy_api.download import Downloader as AniPyDownloader
from anipy_api.provider import LanguageTypeEnum
from colorama import Fore

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
        self.verbose = False

    def download_episode(self, anime: Anime, episode_number: int, language: LanguageTypeEnum = LanguageTypeEnum.SUB,
                         preferred_quality: str = Quality.QUALITY_720P, verbose: bool = False) -> None:
        self.verbose = verbose
        try:
            # prepare stream
            stream = anime.get_video(episode_number, lang=language, preferred_quality=preferred_quality)

            # prepare download path
            anime_dir = Path(os.path.join(self.animes_folder, escape_windows_safe_filename(anime.get_info().name)))
            anime_dir.mkdir(parents=True, exist_ok=True)

            episode_file = os.path.join(anime_dir, str(episode_number))
            download_path = Path(episode_file)

            # download
            downloader = AniPyDownloader(self.__progress_callback, self.__info_callback)
            downloader.download(
                stream=stream,
                download_path=download_path,
                container=".mkv",
                ffmpeg=False
            )
        except:
            raise

    def __info_callback(self, message: str):
        if self.verbose:
            print(f"{Fore.LIGHTBLACK_EX}AniPy-API: {message}")

    def __progress_callback(self, percentage: float):
        self.loader.update_loader(percentage)
        if percentage >= 100:
            print()
