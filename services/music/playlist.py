class Playlist:
    def __init__(self, name: str):
        self.name = name
        self.songs = []

    def __repr__(self):
        return self.name
