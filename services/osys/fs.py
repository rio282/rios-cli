import os
import pickle
import zipfile
from typing import List, Tuple, Dict, Optional


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
        - Ensures the drive letter is uppercase.
        - If the directory starts with a drive letter (e.g., "C:\"), it returns the absolute path.
        - If the directory starts with "~\", it replaces it with the user's home directory.
        - If neither of the above conditions are met, it returns the path relative to the current working directory.

        :param directory: The directory path to be cleaned and converted.
        :return: The absolute path of the given directory.
        """
        directory = (directory
                     .replace("/", "\\")
                     .replace("--use-cache", "")
                     .replace("--dirs", "")
                     .replace("--files", "")
                     .strip())

        # ensure that the drive letter is uppercase
        if len(directory) > 1 and directory[1] == ":":
            directory = directory[0].upper() + directory[1:]

        # real honestly
        if os.path.isabs(directory):
            return os.path.realpath(os.path.abspath(directory))
        elif directory.startswith("~\\"):
            return os.path.realpath(os.path.join(os.path.expanduser("~"), directory.removeprefix("~\\")))
        return os.path.realpath(os.path.join(os.getcwd(), directory))

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

    def zip(self, folder: str) -> Optional[bool]:
        """
        Zips a folder.
        :param folder: the path to the folder that needs to be zipped
        :return: if the operation succeeded
        """
        if not os.path.isdir(folder):
            return False

        try:
            zip_file = f"{folder}.zip"
            with zipfile.ZipFile(file=zip_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=folder)
                        zipf.write(file_path, arcname)
            return True
        except Exception as e:
            raise e

    def unzip(self, zipped_file: str) -> Optional[bool]:
        """
        Unzips a zip folder.
        :param zipped_file: the zip folder to unzip
        :return: if the operation succeeded
        """
        if not os.path.isfile(zipped_file):
            return False

        try:
            with zipfile.ZipFile(file=zipped_file, mode="r") as zip_ref:
                zip_ref.extractall(os.path.dirname(zipped_file))
            return True
        except zipfile.BadZipFile as e:
            raise e

    def view_zip_content(self, zipped_file: str) -> Dict[str, List[Tuple[str, float]]]:
        """
        Returns the content of the zipfile.
        :param zipped_file: The zipfile of which the contents will be viewed of.
        :return: The files and directories of the zipfile within a dictionary.
        """
        if not os.path.isfile(zipped_file):
            raise FileNotFoundError(f"ZIP file '{zipped_file}' not found.")

        try:
            with zipfile.ZipFile(file=zipped_file, mode="r") as zip_ref:
                directories = []
                files = []
                for info in zip_ref.infolist():
                    file_size = info.file_size / (1024 * 1024)  # convert bytes to megabytes
                    if info.is_dir():
                        directories.append(info.filename)
                    else:
                        files.append((info.filename, file_size))

                return {
                    "directories": directories,
                    "files": files
                }
        except Exception as e:
            raise e

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