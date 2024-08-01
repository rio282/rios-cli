import itertools
from typing import Final

import colorama


class Loader:
    def __init__(self, loading_text: str = "Loading:", text_color: colorama.Fore = colorama.Fore.LIGHTGREEN_EX):
        self.loading_text: Final[str] = loading_text
        self.text_color: colorama.Fore = text_color

        self.bar_length: Final[int] = 20
        self.percent_completed: int = 0
        self.text_dot_cycle: itertools.cycle = itertools.cycle(['.', '..', '...'])
        self.spinner_cycle: itertools.cycle = itertools.cycle(['|', '/', '-', '\\'])

    def update_loader(self, progress: float) -> None:
        """
        Sets the loading bar value.
        :param progress: Value between 0 and 100(%).
        """
        if 0 <= progress <= 100:
            self.percent_completed = progress
        else:
            raise ValueError("Progress value must be between 0 and 100")

        self.display_loading_bar()

    def display_loading_bar(self) -> None:
        """
        Displays the loading bar.
        """
        dots = "..." if self.percent_completed == 100 else next(self.text_dot_cycle)
        spaces = " " * (3 - len(dots))
        loading_text = f"{self.loading_text}{dots}{spaces}"

        completed_length = int(self.percent_completed / 100 * self.bar_length)
        empty_length = self.bar_length - completed_length
        bar = f"[{'#' * completed_length}{' ' * empty_length}]"

        spinner = "-" if self.percent_completed == 100 else next(self.spinner_cycle)
        print(f"\r{self.text_color}{loading_text} {bar} {spinner} {self.percent_completed:.2f}%", end="", flush=True)
