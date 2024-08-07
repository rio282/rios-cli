import curses
import random
from time import sleep
from typing import Optional, List, Final

from . import _faker_instance


class Horse:
    def __init__(self, name: Optional[str] = None):
        self.name: Final[str] = name if name else _faker_instance.first_name_female()
        self.distance: int = 0

    def __repr__(self):
        return self.name


class HorseRace:
    def __init__(self, horses: int = 5, update_delay: float = 1 / 15):
        self.horses: Final[List[Horse]] = [Horse() for _ in range(horses)]
        self.update_delay: Final[float] = update_delay
        self.winner: Optional[Horse] = None

    def start(self):
        def race(stdscr):
            screen_height, track_length = stdscr.getmaxyx()
            if len(self.horses) > screen_height:
                raise AttributeError(f"Value 'horses' is too large, max for this screen size: {screen_height}")

            curses.curs_set(0)
            stdscr.clear()

            while not self.winner:
                stdscr.clear()
                for horse in self.horses:
                    horse.distance += random.randint(1, 5)
                    if horse.distance >= track_length:
                        self.winner = horse
                        break

                for idx, horse in enumerate(self.horses):
                    stdscr.addstr(idx, 0, f"{horse.name}: {'-' * horse.distance}🐎")

                stdscr.refresh()
                sleep(self.update_delay)

        curses.wrapper(race)
