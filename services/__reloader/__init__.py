import os
import time
import threading
from typing import List, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import CLI

stop_hot_reloader = False


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, cli_instance: CLI.RiosCLI, ignored_dirs: List[str], debounce_interval: float = 1.0):
        self.cli_instance = cli_instance
        self.ignored_dirs = set(ignored_dirs)
        self.debounce_interval = debounce_interval
        self.debounce_timer = None

    def on_any_event(self, event):
        for ignored_dir in self.ignored_dirs:
            if ignored_dir in event.src_path:
                # exit early
                return

        # Reset the debounce timer
        if self.debounce_timer is not None:
            self.debounce_timer.cancel()

        # Set a new debounce timer
        self.debounce_timer = threading.Timer(self.debounce_interval, self.__trigger_reload, [event])
        self.debounce_timer.start()

    def __trigger_reload(self, event):
        print()
        print("Changes detected!")
        self.cli_instance.do_reload(event)


class HotReloader:

    @staticmethod
    def start(cli_instance: CLI.RiosCLI, root: str = os.getcwd(), ignored_dirs: Optional[List[str]] = None,
              debounce_interval: float = 3.0) -> None:
        if ignored_dirs is None:
            ignored_dirs = ["venv", "__pycache__", ".git", ".idea", ".cache"]

        event_handler = ChangeHandler(cli_instance, ignored_dirs, debounce_interval)
        observer = Observer()
        observer.schedule(event_handler, root, recursive=True)
        observer.start()

        try:
            global stop_hot_reloader
            while not stop_hot_reloader:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        observer.stop()
        observer.join()

    @staticmethod
    def stop() -> None:
        global stop_hot_reloader
        stop_hot_reloader = True
