def escape_windows_safe_filename(unsafe: str) -> str:
    return "".join(x for x in unsafe if x.isalnum())
