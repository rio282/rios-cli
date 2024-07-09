import os
import sys

import pretty_errors
from typing import Final

import tkinter as tk
from tkinter import scrolledtext

from CLI import RiosCLI

PRETTY_ERRORS: Final[bool] = True


def show_error_popup(error):
    def close_window():
        window.destroy()

    window = tk.Tk()
    window.title("Error Information")

    # Window size
    window.geometry("500x300")

    # Error message label
    label = tk.Label(window, text="A fatal error occurred:", font=("Arial", 14))
    label.pack(pady=10)

    # Scrolled text box for error details
    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=10, font=("Arial", 12))
    text_area.pack(pady=10, padx=10)
    text_area.insert(tk.INSERT, str(error))
    text_area.configure(state='disabled')

    # Close button
    close_button = tk.Button(window, text="Close", command=close_window, font=("Arial", 12))
    close_button.pack(pady=10)

    window.eval("tk::PlaceWindow . center")
    window.mainloop()


def is_correct_python_version() -> bool:
    version = sys.version_info
    correct_major_version = version.major >= min_required_python_version["major"]
    correct_minor_version = version.minor >= min_required_python_version["minor"]

    return correct_major_version and correct_minor_version


def main(argc: int, argv: list[str]) -> None:
    try:
        os.system("title Loading...")
        print("Loading...")

        cli = RiosCLI()

        os.system(cli.clear_command)
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

    try:
        main(len(sys.argv), sys.argv)
    except Exception as e:
        show_error_popup(e)
    finally:
        sys.exit(0)
