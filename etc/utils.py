import enum
import os
import re
import threading
from enum import auto
from typing import List, Any, Final, Optional

from fuzzywuzzy import process, fuzz
from playsound import playsound


def escape_windows_safe_filename(unsafe: str) -> str:
    """
    Escapes filenames to make them safe for Windows.
    :param unsafe: Filename to be escaped.
    :return: Windows-safe filename.
    """
    return "".join(x for x in unsafe if x.isalnum())


def truncate_filename(fn: str, fe: str, max_length: int = 32, character: str = "#") -> str:
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
    :param supposed_string: String that's probably an integer
    :return: If the provided object is an integer
    """
    if len(supposed_string) == 0:
        return False

    if supposed_string[0] in ('-', '+'):
        return supposed_string[1:].isdigit()
    return supposed_string.isdigit()


def collapse_spaces(input_str: str) -> str:
    """
    Collapses excessive spaces into a single space character.
    :param input_str: String with many spaces
    :return: String with its spaced collapsed into a single space character
    """
    return re.sub(r"\s+", " ", input_str).strip()


def playsound_deferred(sound_file: str) -> None:
    """
    Plays a sound file asynchronously.
    :param sound_file: File to be played asynchronously
    """
    sound_thread = threading.Thread(target=playsound, args=(sound_file,))
    sound_thread.start()


def get_latest_existing_path(current_directory: str, line: str) -> str:
    path = os.path.join(current_directory, "".join(line.split()[1:]))
    if not os.path.exists(path):
        path = os.path.dirname(path)
    return path


class FuzzyMatcher:
    RECOMMENDED_MATCHING_SCORE: Final[int] = 85
    required_matching_score: int = 50

    @staticmethod
    def _fuzzy_formatter(tokens: List[str]) -> List[str]:
        return [t[0] for t in tokens]

    @staticmethod
    def any_matches(matching_token: str, tokens: List[str], limit: Optional[int] = None) -> List[str]:
        cutoff = limit if limit else FuzzyMatcher.required_matching_score
        matches = process.extractBests(matching_token, tokens, limit=len(tokens), score_cutoff=cutoff)
        return FuzzyMatcher._fuzzy_formatter(matches)


class AutoCompletion:
    TYPE_ALL: Final[enum.auto] = auto()
    TYPE_DIRECTORIES: Final[enum.auto] = auto()
    TYPE_DIRECTORIES_AND_ZIP: Final[enum.auto] = auto()
    TYPE_FILES: Final[enum.auto] = auto()

    MODE_STARTSWITH: Final[enum.auto] = auto()
    MODE_PARTIAL: Final[enum.auto] = auto()
    MODE_MATCH_ANY: Final[enum.auto] = auto()

    @staticmethod
    def path(current_directory: str, text: str, completion_type=TYPE_ALL) -> List[str]:
        if "~" in current_directory:
            current_directory = os.path.join(os.path.expanduser("~"),
                                             current_directory.split("~").pop().removeprefix("\\"))

        def path_filter():
            if not text:
                completion = os.listdir(current_directory)
            else:
                text_lower = text.lower()
                completion = [d for d in os.listdir(current_directory) if d.lower().startswith(text_lower)]

            if completion_type == AutoCompletion.TYPE_DIRECTORIES:
                return [d for d in completion if os.path.isdir(os.path.join(current_directory, d))]
            elif completion_type == AutoCompletion.TYPE_DIRECTORIES_AND_ZIP:
                return [
                    d for d in completion if os.path.isdir(os.path.join(current_directory, d)) or (
                            os.path.isfile(os.path.join(current_directory, d)) and os.path.splitext(d)[1] == ".zip")]
            elif completion_type == AutoCompletion.TYPE_FILES:
                return [d for d in completion if os.path.isfile(os.path.join(current_directory, d))]

            return completion

        # TODO: fix this retarded stuff here
        # return [f"\"{entry}\"" if " " in entry else entry for entry in path_filter()]
        return path_filter()

    @staticmethod
    def matches_of(possible_matches: List[str], text: str, completion_mode=MODE_STARTSWITH) -> List[str]:
        if not text:
            return possible_matches

        text = text.lower()

        if completion_mode == AutoCompletion.MODE_PARTIAL:
            best_match = max(possible_matches, key=lambda match: fuzz.ratio(text, match))
            return [best_match]
        elif completion_mode == AutoCompletion.MODE_MATCH_ANY:
            return FuzzyMatcher.any_matches(text, possible_matches)
        elif completion_mode == AutoCompletion.MODE_STARTSWITH:
            return [entry for entry in possible_matches if entry.lower().startswith(text)]

        # ???
        return possible_matches
