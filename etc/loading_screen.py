from typing import Final


class Loader:
    def __init__(self, loading_text: str = "Loading:"):
        self.loading_text: Final[str] = loading_text
        self.bar_length: Final[int] = 20
        self.percent_completed: int = 0

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
        completed_length = int(self.percent_completed / 100 * self.bar_length)
        empty_length = self.bar_length - completed_length
        bar = f"[{'#' * completed_length}{' ' * empty_length}]"
        print(f"\r{self.loading_text} {bar} {self.percent_completed:.2f}%", end="", flush=True)
