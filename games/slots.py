import curses
import random
from time import sleep

from colorama import Fore


class Slots:
    def __init__(self):
        self.symbols = ["7", "BAR", "🍒", "🍋", "🔔"]
        self.num_reels = 3

        self.longest_symbol = len(max(self.symbols, key=len))
        self.__empty_symbol = " " * self.longest_symbol
        self.results = [self.__empty_symbol for _ in range(self.num_reels)]

        self.spinning = False

    def draw_slot_machine(self, stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        pulls = " ".join([f"[ {pull} ]" for pull in self.results])
        stdscr.addstr(height // 2, width // 2 - len(pulls) // 2, pulls)

        stdscr.addstr(height - 2, 0, "Press '<SPACE>' to spin, 'q' to quit")
        stdscr.refresh()

    def spin_slots(self, stdscr):
        self.spinning = True

        total_duration = 1.75
        num_frames = 50
        max_delay = total_duration / num_frames
        min_delay = 0.05

        # DA SPIN INNIT
        for frame in range(num_frames):
            delay = max_delay - (max_delay - min_delay) * (frame / num_frames)

            for i in range(self.num_reels):
                self.results[i] = str(random.choice(self.symbols)).center(self.longest_symbol)
            self.draw_slot_machine(stdscr)

            sleep(delay)

        # FINAL RESULTS
        for i in range(self.num_reels):
            self.results[i] = str(random.choice(self.symbols)).center(self.longest_symbol)
        self.draw_slot_machine(stdscr)
        sleep(0.5)

        self.spinning = False

    def play(self):
        def inner(stdscr):
            curses.curs_set(0)
            stdscr.nodelay(1)

            while True:
                self.draw_slot_machine(stdscr)

                # FIXME: yo why tf is this not working, am i tweaking?
                if not self.spinning:
                    key = stdscr.getch()
                    if key == ord('q'):
                        break
                    elif key == ord(' '):
                        self.spin_slots(stdscr)

                if len(set(self.results)) == 1 and self.results[0] != self.__empty_symbol:
                    stdscr.addstr(0, 0, "JACKPOT! Press any key to continue...")
                    stdscr.refresh()
                    stdscr.getch()
                    break

        win = curses.wrapper(inner)
        if win:
            print(f"{Fore.GREEN}You won the JACKPOT!!!")
        else:
            print(F"{Fore.RED}Better luck next time!")
