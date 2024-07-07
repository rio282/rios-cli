import os
from typing import List, Tuple, Dict


class FileSystem:
    def __init__(self):
        self.file_cache: Dict[str, List[Tuple[str, float]]] = {}
        self.directory_cache: Dict[str, List[str]] = {}

    def __clean_directory(self, directory: str) -> str:
        directory = directory.replace(":", ":\\")
        if directory.startswith("C:\\"):
            return os.path.abspath(directory)
        elif directory.startswith("~\\"):
            return os.path.join(os.path.expanduser("~"), directory.removeprefix("~\\"))
        return os.path.join(os.getcwd(), directory)

    def get_files_in_directory(self, directory: str) -> List[Tuple[str, float]] or None:
        """
        Gets the files within a directory along with their respective file size in Megabytes.
        If anything fails an error will be thrown with a corresponding error message.

        :param directory: the directory of which the files are requested
        :return: Returns a list of tuples that contain: [filename, file_size] in this order
        """
        directory = self.__clean_directory(directory)

        # checks if dir exists
        if directory and not os.path.exists(directory):
            if directory in self.directory_cache:
                # remove from cache if dir doesn't exist anymore
                self.directory_cache.pop(directory)
            raise NotADirectoryError(f"Directory '{directory}' doesn't exist.")

        # checks if dir is available in cache
        if directory in self.directory_cache:
            return self.directory_cache[directory]

        files = []
        for entry in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, entry)):
                file_size = os.stat(os.path.join(directory, entry)).st_size / (1024 * 1024)
                files.append((entry, file_size))

        # save to cache before returning
        self.file_cache[directory] = files
        return files

    def get_directories_in_directory(self, directory: str) -> List[str] or None:
        """
        Gets the directories within a directory.
        If anything fails an error will be thrown with a corresponding error message.

        :param directory: the directory of which the directories are requested
        :return: Returns a list of directories' names
        """
        directory = self.__clean_directory(directory)

        # checks if dir exists
        if directory and not os.path.exists(directory):
            if directory in self.directory_cache:
                self.directory_cache.pop(directory)
            raise NotADirectoryError(f"Directory '{directory}' doesn't exist.")

        # checks if dir is available in cache
        if directory in self.directory_cache:
            return self.directory_cache[directory]

        directories = []
        for entry in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, entry)):
                directories.append(entry)

        # save to cache before returning
        self.directory_cache[directory] = directories
        return directories

    def save_cache(self, cache_file: str) -> None:
        raise NotImplementedError
