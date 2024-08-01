import os
from datetime import datetime
from typing import Dict, Any

import yt_dlp

from etc import escape_windows_safe_filename
from etc.loading_screen import Loader


class Downloader:
    def __init__(self):
        self.file_size: int = -1
        self.percent_completed: float = -1.0

        self.music_folder: str = os.path.expanduser("~/Music")
        self.video_folder: str = os.path.expanduser("~/Videos")

        self.loader: Loader = Loader("Downloading")

    def download(self, url: str, audio_only: bool = False) -> bool:
        print("Preparing...")
        filename = escape_windows_safe_filename(str(datetime.now()))
        download_dir = self.music_folder if audio_only else self.video_folder
        ydl_opts = {
            "quiet": True,
            "restrictfilenames": True,
            "noprogress": True,
            "no_warnings": True,
            "format": "bestaudio" if audio_only else "bestvideo+bestaudio",
            "outtmpl": os.path.join(download_dir, f"{filename}.%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [self.__download_callback],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }] if audio_only else [],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("Collecting video information...")
                video_info = ydl.extract_info(url, download=False)
                video_title = video_info["title"]
                print(f"Video found: {video_title} @ {url}")

                filename = f"{filename}.{'mp3' if audio_only else 'mp4'}"
                full_path = os.path.join(download_dir, filename)

                if os.path.exists(full_path):
                    return False

                self.file_size = video_info.get("filesize") or video_info.get("filesize_approx")
                ydl.download([url])
                print("\nFinalizing...")

            print(f"File downloaded to: {full_path}")
            return True

        except yt_dlp.utils.DownloadError as e:
            print(f"Error during download: {e}")
            return False

    def __download_callback(self, download_data: Dict[str, Any]) -> None:
        if download_data["status"] == "downloading":
            percent_str = (download_data.get("_percent_str", "0.0%")
                           .strip()
                           .replace("\x1b[0;94m", "")
                           .replace("\x1b[0m", "")
                           .removesuffix("%"))

            self.percent_completed = float(percent_str)
            self.loader.update_loader(self.percent_completed)
