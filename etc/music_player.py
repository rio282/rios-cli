from time import sleep
from queue import Queue
from threading import Thread

from colorama import Fore

import vlc


class MusicPlayer:
    def __init__(self):
        self.queue = Queue()
        self.playing = False
        self.player_thread = None

    def play(self, audio_file: str) -> None:
        if self.playing:
            self.queue.put(audio_file)
            print(f"{Fore.LIGHTGREEN_EX}Added {audio_file} to the queue.")
        else:
            self.playing = True
            print(f"{Fore.GREEN}Playing {audio_file}")
            self.player_thread = Thread(target=self.__play_audio, args=(audio_file,))
            self.player_thread.start()

    def __play_audio(self, audio_file: str):
        vlc_instance = vlc.Instance("--no-xlib")
        player = vlc_instance.media_player_new()

        while True:
            media = vlc_instance.media_new(audio_file)
            player.set_media(media)

            player.play()
            while player.is_playing():
                sleep(0.1)

            player.release()
            media.release()

            if not self.queue.empty():
                audio_file = self.queue.get()
                print(f"{Fore.LIGHTGREEN_EX}Playing next song: {audio_file}")
            else:
                self.playing = False
                print(Fore.RED + "Queue is empty.")
                break

    def next_song(self) -> None:
        if not self.queue.empty():
            next_song = self.queue.get()
            print(f"{Fore.GREEN}Playing next song: {next_song}")
        else:
            self.playing = False
            print(Fore.RED + "Queue is empty.")
