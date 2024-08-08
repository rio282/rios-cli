import json
from _thread import RLock
from typing import Any


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
