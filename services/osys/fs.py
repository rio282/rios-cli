import json
import os
import pickle
import zipfile
from typing import List, Tuple, Dict, Optional, Any
import win32api
from win32con import HKEY_CLASSES_ROOT


class File:
    def __init__(self, name: str, location: str, size_mb: float, last_updated: float):
        self.name = name
        self.location = location
        self.size_mb = size_mb
        self.last_updated = last_updated

    def __repr__(self):
        return f"{os.path.join(self.location, self.name)} | ~{self.size_mb:.2f}MB | {self.last_updated}"


class FileEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, File):
            return {
                "name": obj.name,
                "location": obj.location,
                "size_mb": obj.size_mb,
                "last_updated": obj.last_updated
            }
        return super().default(obj)


class FileSystem:
    def __init__(self, cache_dir: str):
        self.cache_file = f"{cache_dir}/ls.cache"
        self.file_cache: Dict[str, List[File]] = {}
        self.directory_cache: Dict[str, List[str]] = {}

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
                     .replace("--inspect-cache", "")
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

    @staticmethod
    def get_file_type(extension: str) -> str:
        """
        Gets the name/mimetype of the file extension supplied.

        :param extension: A file extension
        :return: The name the extension corresponds with in the system
        """
        try:
            key = win32api.RegOpenKey(HKEY_CLASSES_ROOT, extension)
            file_type_class, _ = win32api.RegQueryValueEx(key, "")

            key = win32api.RegOpenKey(HKEY_CLASSES_ROOT, file_type_class)
            file_type_description, _ = win32api.RegQueryValueEx(key, "")

            return file_type_description
        except:
            return extension.removeprefix(".")

    def get_files_in_directory(self, directory: str, use_cache: bool = False) -> List[File]:
        """
        Gets the files within a directory along with their respective file size in Megabytes.
        If anything fails an error will be thrown with a corresponding error message.

        :param directory: The directory of which the files are requested.
        :param use_cache: Makes call use the cache (if available) instead of checking again.
        :return: Returns a list of files (class File).
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
                full_path = os.path.join(directory, entry)
                file_size = os.stat(full_path).st_size / (1024 * 1024)
                last_updated = os.path.getmtime(full_path)
                files.append(File(name=entry, location=directory, size_mb=file_size, last_updated=last_updated))

        # save to cache before returning
        self.file_cache[directory] = files
        return files

    def get_directories_in_directory(self, directory: str, use_cache: bool = False) -> List[str]:
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

    def get_zip_content(self, zipped_file: str) -> Dict[str, List[Tuple[str, float]]]:
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

    def get_file_content(self, file: str, as_list: bool = True) -> List[str] or str:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"File '{file}' not found.")

        with open(file, mode="r") as _file:
            if as_list:
                return _file.readlines()
            return _file.read()

    def get_file_content_binary(self, file: str) -> Dict[str, Any]:
        with open(file=file, mode="rb") as f:
            return pickle.load(f)

    def save(self) -> None:
        """
        Saves the cache to a file.
        """
        try:
            with open(file=self.cache_file, mode="wb") as f:
                pickle.dump({"file_cache": self.file_cache, "directory_cache": self.directory_cache}, f)
        except Exception as e:
            print("Couldn't save cache.")
            print(e)

    def load(self) -> None:
        """
        Loads the cache from a file.
        """
        if os.path.exists(self.cache_file):
            with open(file=self.cache_file, mode="rb") as f:
                cache_data = pickle.load(f)
                self.file_cache = cache_data.get("file_cache", {})
                self.directory_cache = cache_data.get("directory_cache", {})
