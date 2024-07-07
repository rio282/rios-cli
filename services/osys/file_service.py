import os
import pickle
from typing import List, Tuple, Dict


class FileSystem:
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.file_cache: Dict[str, List[Tuple[str, float]]] = {}
        self.directory_cache: Dict[str, List[str]] = {}
        self.load_cache()

    @staticmethod
    def clean_directory(directory: str) -> str:
        """
        Cleans and converts a given directory path to an absolute path.

        The method processes the input directory path to ensure it is in the correct format:
        - Converts forward slashes to backward slashes for consistency.
        - If the directory starts with "C:\", it returns the absolute path.
        - If the directory starts with "~\", it replaces it with the user's home directory.
        - If neither of the above conditions are met, it returns the path relative to the current working directory.

        :param directory: The directory path to be cleaned and converted.
        :return: The absolute path of the given directory.
        """
        directory = directory.replace("/", "\\")
        if directory.startswith("C:\\"):
            return os.path.abspath(directory)
        elif directory.startswith("~\\"):
            return os.path.join(os.path.expanduser("~"), directory.removeprefix("~\\"))
        return os.path.join(os.getcwd(), directory)

    def get_files_in_directory(self, directory: str, use_cache: bool = False) -> List[Tuple[str, float]] or None:
        """
        Gets the files within a directory along with their respective file size in Megabytes.
        If anything fails an error will be thrown with a corresponding error message.

        :param directory: The directory of which the files are requested.
        :param use_cache: Makes call use the cache (if available) instead of checking again.
        :return: Returns a list of tuples that contain: [filename, file_size] in this order.
        """
        directory = self.clean_directory(directory)

        # checks if dir exists
        if directory and not os.path.exists(directory):
            if directory in self.directory_cache:
                # remove from cache if dir doesn't exist anymore
                self.directory_cache.pop(directory)
            raise NotADirectoryError(f"Directory '{directory}' doesn't exist.")

        # checks if dir is available in cache
        if use_cache and directory in self.file_cache:
            return self.file_cache[directory]

        files = []
        for entry in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, entry)):
                file_size = os.stat(os.path.join(directory, entry)).st_size / (1024 * 1024)
                files.append((entry, file_size))

        # save to cache before returning
        self.file_cache[directory] = files
        return files

    def get_directories_in_directory(self, directory: str, use_cache: bool = False) -> List[str] or None:
        """
        Gets the directories within a directory.
        If anything fails an error will be thrown with a corresponding error message.

        :param directory: The directory of which the directories are requested.
        :param use_cache: Makes call use the cache (if available) instead of checking again.
        :return: Returns a list of directories' names.
        """
        directory = self.clean_directory(directory)

        # checks if dir exists
        if directory and not os.path.exists(directory):
            if directory in self.directory_cache:
                self.directory_cache.pop(directory)
            raise NotADirectoryError(f"Directory '{directory}' doesn't exist.")

        # checks if dir is available in cache
        if use_cache and directory in self.directory_cache:
            return self.directory_cache[directory]

        directories = []
        for entry in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, entry)):
                directories.append(entry)

        # save to cache before returning
        self.directory_cache[directory] = directories
        return directories

    def save_cache(self) -> None:
        """
        Saves the cache to a file.
        """
        try:
            with open(file=self.cache_file, mode="wb") as f:
                pickle.dump({"file_cache": self.file_cache, "directory_cache": self.directory_cache}, f)
        except Exception as e:
            print("Couldn't save cache.")
            print(e)

    def load_cache(self) -> None:
        """
        Loads the cache from a file.
        """
        if os.path.exists(self.cache_file):
            with open(file=self.cache_file, mode="rb") as f:
                cache_data = pickle.load(f)
                self.file_cache = cache_data.get("file_cache", {})
                self.directory_cache = cache_data.get("directory_cache", {})
