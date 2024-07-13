import os
from queue import PriorityQueue
from typing import Optional

from colorama import Fore

from services import file_system
from services.music.playlist import Playlist
from services.music.song import Song


class MusicPlayer:
    def __init__(self):
        self.now_playing: Optional[Song] = None
        self.current_playlist: Optional[Playlist] = None
        self.queue: PriorityQueue = PriorityQueue()

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
            song_name = song_file[0]
            if song_name.endswith(".mp3"):
                location = os.path.join(playlist_folder, song_name)
                name = song_name.split(".")
                name = name[len(name) - 2]

                _playlist.songs.append(Song(name, location))

        return _playlist

    def play_playlist(self, _playlist: Playlist) -> None:
        for _song in _playlist.songs:
            self.play_song(_song, from_playlist=_playlist)

    def play_song(self, _song: Song, from_playlist: Optional[Playlist] = None) -> None:
        self.now_playing = _song
        self.current_playlist = from_playlist
        # TODO: actually play it lol

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
