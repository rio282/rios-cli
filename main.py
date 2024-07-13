import os
import sys
import argparse
import threading

import pretty_errors
from typing import Final

import tkinter as tk
from tkinter import scrolledtext
import webbrowser

from CLI import RiosCLI
from services.__reloader import HotReloader

PRETTY_ERRORS: Final[bool] = True


def show_error_popup(error: Exception or str) -> None:
    def close_window():
        window.destroy()

    def reload():
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def search_on_google():
        query = str(error).replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    window = tk.Tk()
    window.title("Error Information")
    window.geometry("500x300")

    # error details
    label = tk.Label(window, text="A fatal error occurred:", font=("Arial", 14))
    label.pack(pady=10)

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=60, height=10, font=("Arial", 12))
    text_area.pack(pady=10, padx=10)
    text_area.insert(tk.INSERT, str(error))
    text_area.configure(state="disabled")

    # button frame
    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    # close button
    close_button = tk.Button(button_frame, text="Close", command=close_window, font=("Arial", 12))
    close_button.grid(row=0, column=0, padx=5)

    # reload button
    reload_button = tk.Button(button_frame, text="Reload Application", command=reload, font=("Arial", 12))
    reload_button.grid(row=0, column=1, padx=5)

    # search on Google button
    search_button = tk.Button(button_frame, text="Search on Google", command=search_on_google, font=("Arial", 12))
    search_button.grid(row=0, column=2, padx=5)

    window.eval("tk::PlaceWindow . center")
    window.mainloop()


def is_correct_python_version() -> bool:
    version = sys.version_info
    correct_major_version = version.major >= min_required_python_version["major"]
    correct_minor_version = version.minor >= min_required_python_version["minor"]

    return correct_major_version and correct_minor_version


def main(argc: int, argv: argparse.Namespace) -> None:
    try:
        # loading text
        os.system("title Loading...")
        print("Loading...")

        # setup
        cli = RiosCLI()

        if argc > 0:
            print("OPTIONS:")
            if argv.enable_hot_reloading:
                print("WITH: Hot reloading")
                watcher_thread = threading.Thread(target=HotReloader.start, args=(cli,))
                watcher_thread.daemon = True
                watcher_thread.start()

        # clear & start
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
        parser = argparse.ArgumentParser(description="R-CLI with optional hot reloading")
        parser.add_argument("--enable-hot-reloading", action="store_true", help="Enable hot reloading")
        args = parser.parse_args()
        main(len(sys.argv), args)
    except Exception as e:
        # fatal error
        show_error_popup(e)
    finally:
        HotReloader.stop()
        sys.exit(0)
