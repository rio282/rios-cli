import curses
import random
from time import sleep


class Slots:
    def __init__(self):
        self.symbols = ["7", "BAR", "🍒", "🍋", "🔔"]
        self.num_reels = 3

        self.longest_symbol = len(max(self.symbols, key=len))
        self.__empty_symbol = " " * self.longest_symbol
        self.results = [self.__empty_symbol for _ in range(self.num_reels)]

    def draw_slot_machine(self, stdscr):
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        pulls = " ".join([f"[ {pull} ]" for pull in self.results])
        stdscr.addstr(height // 2, width // 2 - len(pulls) // 2, pulls)

        stdscr.addstr(height - 2, 0, "Press '<SPACE>' to spin, 'q' to quit")
        stdscr.refresh()

    def spin_slots(self):
        for i in range(self.num_reels):
            result = str(random.choice(self.symbols)).center(self.longest_symbol)
            self.results[i] = result

    def play(self):
        def inner(stdscr):
            curses.curs_set(0)
            stdscr.nodelay(1)
            stdscr.timeout(100)

            while True:
                self.draw_slot_machine(stdscr)
                key = stdscr.getch()

                if key == ord('q'):
                    break
                elif key == ord(' '):
                    self.spin_slots()
                    self.draw_slot_machine(stdscr)
                    sleep(0.5)

                if len(set(self.results)) == 1 and self.results[0] != self.__empty_symbol:
                    stdscr.addstr(0, 0, "JACKPOT! Press any key to continue...")
                    stdscr.getch()
                    break

        curses.wrapper(inner)
