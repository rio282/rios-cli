import json
from _thread import RLock
from typing import Any, Optional, List


class SerializedEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        # handle user-defined objects by converting their __dict__ to a dict. legit...
        if hasattr(obj, "__dict__"):
            return {k: v for k, v in obj.__dict__.items() if
                    not k.startswith("_") and not isinstance(v, (property, RLock))}

        # handle sets by converting them to lists
        if isinstance(obj, set) or isinstance(obj, frozenset):
            return list(obj)

        # handle bytes by decoding into a string
        if isinstance(obj, bytes):
            return obj.decode("utf-8")

        # etc.
        return self.default(obj)


class CommandArgsParser:
    def __init__(self, line: str):
        self.line = line.strip()
        self.args = line.split()
        self.args_raw = [self.__remove_arg_prefix(arg) for arg in self.args]

    def __add_arg_prefix(self, arg: str) -> str:
        return arg if arg.startswith("--") else f"--{arg}"

    def __remove_arg_prefix(self, arg: str) -> str:
        return arg.removeprefix("--")

    def is_arg_present(self, arg: str) -> bool:
        return self.__remove_arg_prefix(arg) in self.args_raw

    def is_arg_present_exclusive(self, arg: str, from_other: List[str] or str) -> bool:
        if isinstance(from_other, str):
            from_other = [from_other]

        arg = self.__remove_arg_prefix(arg)
        return self.is_arg_present(arg) and arg not in from_other

    def get_value_of_arg(self, arg: str) -> Optional[str]:
        if not self.is_arg_present(arg):
            return None

        pos = self.args_raw.index(self.__remove_arg_prefix(arg))
        val = pos + 1

        if val >= len(self.args):
            return None

        return self.args[val]

    @property
    def has_args(self) -> bool:
        return len(self.args_raw) > 0
