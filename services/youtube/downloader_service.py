import os.path

import pytube.request
from pytube import YouTube, Stream

from moviepy.editor import AudioFileClip

from etc.loading_screen import Loader
from etc import escape_windows_safe_filename
from etc.menu import InteractiveMenu


class Downloader:
    def __init__(self):
        pytube.request.default_range_size = 8_388_608  # 8 MB

        self.video_id: str or None = None
        self.file_size: int = -1
        self.percent_completed = -1

        self.music_folder = os.path.expanduser("~/Music")
        self.video_folder = os.path.expanduser("~/Videos")

        self.loader = Loader("Downloading...")

    def download(self, url: str, audio_only: bool = False) -> bool:
        file_format = "webm" if audio_only else "mp4"

        # prepare
        print("Preparing...")
        yt = YouTube(url, on_progress_callback=self.__download_callback)
        filename = f"{escape_windows_safe_filename(yt.title)}.{file_format}"
        if os.path.exists(filename):
            return False

        self.video_id = yt.video_id
        self.file_size = yt.streams.get_highest_resolution().filesize

        # download
        streams = yt.streams.filter(file_extension=file_format)
        if audio_only:
            streams = streams.filter(only_audio=True)
        else:
            streams = streams.filter(progressive=True)
            streams = streams.order_by("resolution").desc()

        download_path = self.music_folder if audio_only else self.video_folder
        stream = streams.first()
        stream.download(output_path=download_path, filename=filename)

        # done
        downloaded_location = os.path.join(download_path, filename)
        print(f"\n\nFile downloaded to: {downloaded_location}")

        if audio_only:
            self.prompt_audio_file_conversion(downloaded_location)

        return True

    def prompt_audio_file_conversion(self, file_path: str, old_file_format: str = "webm",
                                     new_file_format: str = "mp3") -> None:
        result = InteractiveMenu.spawn(["Yes", "No"], "Do you wish to convert to mp3?")
        wants_mp3_conversion = result.lower() == "yes"
        if wants_mp3_conversion:
            new_file_path = file_path.replace(old_file_format, new_file_format)
            audio_clip = AudioFileClip(file_path)
            audio_clip.write_audiofile(new_file_path)
            os.remove(file_path)

    def __download_callback(self, stream: Stream, chunk: bytes, bytes_remaining: int) -> None:
        self.percent_completed = ((self.file_size - bytes_remaining) / self.file_size) * 100
        self.loader.update_loader(self.percent_completed)
