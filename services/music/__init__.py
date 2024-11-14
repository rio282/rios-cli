import os
import threading
from time import sleep
from queue import PriorityQueue
from typing import Optional

import pygame
from colorama import Fore
from deprecation import deprecated

from services import file_system
from services.music.playlist import Playlist
from services.music.song import Song


@deprecated
class MusicPlayer:
    def __init__(self):
        self.now_playing: Optional[Song] = None
        self.queue: PriorityQueue = PriorityQueue()
        self.current_playlist: Optional[Playlist] = None
        self.playlist_thread: Optional[threading.Thread] = None
        self.is_paused: bool = False
        pygame.init()
        pygame.mixer.init()

    @staticmethod
    def load_playlist_by_name(playlist_name: str) -> Optional[Playlist]:
        _playlist = Playlist(playlist_name)

        try:
            playlist_folder = os.path.join(os.path.expanduser("~/Music"), "Playlists", playlist_name)
            playlist_files = file_system.get_files_in_directory(playlist_folder)
        except NotADirectoryError:
            print(f"{Fore.RED}Playlist '{playlist_name}' doesn't exist.")
            return

        for song_file in playlist_files:
            song_name = song_file.name
            if song_name.endswith(".mp3"):
                location = os.path.join(playlist_folder, song_name)
                name = song_name.split(".")
                name = name[len(name) - 2]

                _playlist.songs.append(Song(name, location))

        return _playlist

    def play_playlist(self, _playlist: Playlist) -> None:
        if self.playlist_thread and self.playlist_thread.is_alive():
            print("A playlist is already playing. Please stop the current playlist before starting a new one.")
            return

        self.playlist_thread = threading.Thread(target=self._play_playlist_in_background, args=(_playlist,))
        self.playlist_thread.start()

    def _play_playlist_in_background(self, _playlist: Playlist) -> None:
        for _song in _playlist.songs:
            self.play_song(_song, from_playlist=_playlist)
            while pygame.mixer.music.get_busy() or self.is_paused:
                # wait for song to finish or resume from pause
                # reduce sleep time while paused to improve responsiveness
                sleep(0.1 if self.is_paused else 1)

    def play_song(self, _song: Song, from_playlist: Optional[Playlist] = None) -> None:
        self.now_playing = _song
        self.current_playlist = from_playlist
        pygame.mixer.music.load(_song.location)
        pygame.mixer.music.play()

    def add_song_to_queue(self, _song: Song) -> None:
        self.queue.put(_song)

    def remove_song_from_queue(self, _song: Song) -> Optional[Song]:
        found_song = None

        for _ in range(self.queue.qsize()):
            current_song = self.queue.get()
            if current_song == _song:
                found_song = current_song
            else:
                self.queue.put(current_song)

        return found_song

    def pause(self) -> None:
        pygame.mixer.music.pause()
        self.is_paused = True

    def resume(self) -> None:
        pygame.mixer.music.unpause()
        self.is_paused = False

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self.now_playing = None
        self.current_playlist = None
        self.queue = PriorityQueue()
        if self.playlist_thread and self.playlist_thread.is_alive():
            self.playlist_thread.join()

    def next(self) -> None:
        if not self.now_playing:
            return

        # check if there's a song in the queue
        if not self.queue.empty():
            next_song = self.queue.get()
            self.play_song(next_song)
            return

        # no song in the queue -> check if there's a current playlist
        if self.current_playlist:
            current_index = self.current_playlist.songs.index(self.now_playing)
            if current_index < len(self.current_playlist.songs) - 1:
                next_song = self.current_playlist.songs[current_index + 1]
                self.play_song(next_song, from_playlist=self.current_playlist)

        # queue empty


music_player = MusicPlayer()
