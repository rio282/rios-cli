import os
import sys
import socket

import pretty_errors
from typing import Final

from CLI import RiosCLI

ENVIRONMENT: Final[str] = "dev"
LOCALHOST: Final[str] = "127.0.0.1"
PRETTY_ERRORS: Final[bool] = True

SERVER_ADDRESS_LOCAL: Final[str] = socket.gethostbyname(socket.gethostname())
SERVER_ADDRESS_PUBLIC: Final[str] = "UNKNOWN"  # TODO
WEB_SERVER_PORT: Final[int] = 8000
ETC_SERVER_PORT: Final[int] = 55555


def is_correct_python_version() -> bool:
    version = sys.version_info
    correct_major_version = version.major >= min_required_python_version["major"]
    correct_minor_version = version.minor >= min_required_python_version["minor"]

    return correct_major_version and correct_minor_version


def main(argc: int, argv: list[str]) -> None:
    try:
        cli = RiosCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\nExit via KeyboardInterrupt (CTRL+C).")
    except Exception as ex:
        raise ex
    finally:
        print("Cya!")


if __name__ == "__main__":
    if PRETTY_ERRORS:  # :3
        pretty_errors.configure(
            filename_display=pretty_errors.FILENAME_FULL,
            line_number_first=True,
            display_link=True,
            line_color=f"{pretty_errors.RED} > {pretty_errors.default_config.line_color}",
            code_color=f"  {pretty_errors.default_config.line_color}",
            truncate_code=True,
            display_locals=True
        )

    # check the minimum required python version
    min_required_python_version: Final[dict[str, int]] = {
        "major": 3,
        "minor": 11
    }
    if not is_correct_python_version():
        raise EnvironmentError(
            f"Incorrect Python version. Min required: {min_required_python_version['major']}.{min_required_python_version['minor']}.0"
        )

    clear_command = "cls" if os.name == "nt" else "clear"

    # main & exit
    main(len(sys.argv), sys.argv)
    sys.exit(0)
