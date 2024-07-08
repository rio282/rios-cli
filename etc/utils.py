import os
from typing import Final, List


def escape_windows_safe_filename(unsafe: str) -> str:
    """
    Escapes filenames to make them safe for Windows.
    :param unsafe: Filename to be escaped.
    :return: Windows-safe filename.
    """
    return "".join(x for x in unsafe if x.isalnum())


def truncate_filename(fn: str, fe: str, max_length: int = 32, character: str = ">") -> str:
    """
    Truncates filenames safely.
    :param fn: filename
    :param fe: file extension
    :param max_length: cut-off length
    :param character: character to show when the filename is truncated.
    :return: truncated filename
    """
    from colorama import Fore

    combined_length = len(fn) + len(fe)
    if combined_length >= max_length:
        truncate_length = max_length - len(fe) - 3  # 3 characters for >>>
        fn = fn[:truncate_length] + (character * 3)

    return f"{fn}{Fore.LIGHTBLACK_EX}{fe}{Fore.RESET}"


class AutoCompletion:
    BOTH: Final[str] = "BOTH"
    DIRECTORIES: Final[str] = "DIRECTORIES"
    FILES: Final[str] = "FILES"

    @staticmethod
    def autocomplete_path(current_directory: str, text: str, line: str, begidx: int, endidx: int,
                          completion_type: str = BOTH) -> List[str]:
        if not text:
            completion = os.listdir(current_directory)
        else:
            text_lower = text.lower()
            completion = [d for d in os.listdir(current_directory) if d.lower().startswith(text_lower)]

        if completion_type == AutoCompletion.DIRECTORIES:
            return [d for d in completion if os.path.isdir(os.path.join(current_directory, d))]
        elif completion_type == AutoCompletion.FILES:
            return [d for d in completion if os.path.isfile(os.path.join(current_directory, d))]

        return completion
