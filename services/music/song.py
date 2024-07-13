class Song:
    def __init__(self, name: str, location: str):
        self.name = name
        self.location = location

    def __repr__(self):
        return f"{self.name} at {self.location}"
