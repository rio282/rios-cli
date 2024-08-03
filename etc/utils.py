import os
import re
from enum import auto
from typing import List, Any

from fuzzywuzzy import process, fuzz


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


def is_integer(supposed_string: Any) -> bool:
    """
    Checks if the provided string is an integer.
    :param supposed_string: string that's probably an integer
    :return: If the provided object is an integer
    """
    if supposed_string[0] in ('-', '+'):
        return supposed_string[1:].isdigit()
    return supposed_string.isdigit()


def collapse_spaces(input_str: str) -> str:
    """
    Collapses excessive spaces into a single space character.
    :param input_str: String with many spaces
    :return:
    """
    return re.sub(r"\s+", " ", input_str).strip()


class FuzzyMatcher:
    @staticmethod
    def top(input_str: str, potential_matches: List[str], top_size: int = 1) -> List[str]:
        matches = process.extract(input_str, potential_matches, limit=top_size)
        return [match[0] for match in matches]

    @staticmethod
    def any_matches(input_str: str, potential_matches: List[str]) -> List[str]:
        matches = process.extract(input_str, potential_matches)
        return [match[0] for match in matches if match[1] > 0]


class AutoCompletion:
    TYPE_BOTH = auto()
    TYPE_DIRECTORIES = auto()
    TYPE_FILES = auto()

    MODE_STARTSWITH = auto()
    MODE_PARTIAL = auto()
    MODE_MATCH_ANY = auto()

    @staticmethod
    def path(current_directory: str, text: str, line: str, begidx: int, endidx: int,
             completion_type=TYPE_BOTH) -> List[str]:
        if not text:
            completion = os.listdir(current_directory)
        else:
            text_lower = text.lower()
            completion = [d for d in os.listdir(current_directory) if d.lower().startswith(text_lower)]

        if completion_type == AutoCompletion.TYPE_DIRECTORIES:
            return [d for d in completion if os.path.isdir(os.path.join(current_directory, d))]
        elif completion_type == AutoCompletion.TYPE_FILES:
            return [d for d in completion if os.path.isfile(os.path.join(current_directory, d))]

        return completion

    @staticmethod
    def matches_of(possible_matches: List[str], text: str, line: str, begidx: int, endidx: int,
                   completion_mode=MODE_STARTSWITH) -> List[str]:
        if not text:
            return possible_matches

        text = text.lower()

        if completion_mode == AutoCompletion.MODE_PARTIAL:
            best_match = max(possible_matches, key=lambda match: fuzz.ratio(text, match))
            return [best_match]
        elif completion_mode == AutoCompletion.MODE_MATCH_ANY:
            return FuzzyMatcher.any_matches(text, possible_matches)

        return [entry for entry in possible_matches if entry.lower().startswith(text)]
