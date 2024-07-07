def escape_windows_safe_filename(unsafe: str) -> str:
    """
    Escapes filenames to make them safe for Windows.
    :param unsafe: Filename to be escaped.
    :return: Windows-safe filename.
    """
    return "".join(x for x in unsafe if x.isalnum())
