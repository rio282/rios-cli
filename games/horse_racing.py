import curses
import random
from time import sleep
from typing import Optional, List, Final

from deprecation import deprecated

from . import _faker_instance


@deprecated
class Horse:
    def __init__(self, name: Optional[str] = None):
        self.name: Final[str] = name if name else _faker_instance.first_name_female()
        self.distance: int = 0

    def __repr__(self):
        return self.name


@deprecated
class HorseRace:
    def __init__(self, horses: int = 5, update_delay: float = 1 / 15):
        self.horses: Final[List[Horse]] = [Horse() for _ in range(horses)]
        self.update_delay: Final[float] = update_delay
        self.winner: Optional[Horse] = None
        self.winning_number: Optional[int] = None

    def __get_longest_name_length(self) -> int:
        return len(max(self.horses, key=lambda _horse: len(_horse.name)).name)

    def start(self):
        def inner(stdscr):
            screen_height, screen_width = stdscr.getmaxyx()
            if len(self.horses) > screen_height - 1:
                raise AttributeError(f"Value 'horses' is too large, max for this screen size: {screen_height - 1}")

            curses.curs_set(0)
            stdscr.clear()

            longest_name = self.__get_longest_name_length()
            finish_line = screen_width - longest_name - 3
            while not self.winner:
                stdscr.clear()

                # check for a winner
                for idx, horse in enumerate(self.horses):
                    horse.distance += random.randint(0, 5)
                    if horse.distance >= finish_line:
                        self.winner = horse
                        self.winning_number = idx + 1
                        horse.distance = finish_line
                        break

                # calculate new position
                for idx, horse in enumerate(self.horses):
                    padded_name = horse.name.ljust(longest_name)
                    track_position = len(padded_name) + 2
                    stdscr.addstr(idx, 0, padded_name)
                    stdscr.addstr(idx, track_position, f"{'-' * horse.distance}🐎")

                # draw finish line
                for i in range(len(self.horses)):
                    stdscr.addstr(i, finish_line + longest_name, "🏁")

                # yahh, it's rewind time...
                stdscr.refresh()
                sleep(self.update_delay)

        curses.wrapper(inner)
