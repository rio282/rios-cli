import curses
from typing import List, Optional


class InteractiveMenu:
    @staticmethod
    def spawn(with_options: List[str], title: Optional[str] = None) -> Optional[str]:
        def menu(stdscr):
            stdscr.clear()

            curses.curs_set(0)  # hide cursor
            stdscr.keypad(True)  # enable keypad mode
            curses.start_color()  # enable color
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

            current_row = 0
            while True:
                stdscr.clear()

                if title:
                    stdscr.addstr(0, 0, title, curses.color_pair(2))

                # print menu options
                for index, row in enumerate(with_options):
                    if index == current_row:
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(index + 2, 0, f"[{index + 1}] {row}")
                        stdscr.attroff(curses.color_pair(1))
                    else:
                        stdscr.addstr(index + 2, 0, f"[{index + 1}] {row}")

                # update selection
                key = stdscr.getch()
                if key == curses.KEY_UP and current_row > 0:
                    current_row -= 1
                elif key == curses.KEY_DOWN and current_row < len(with_options) - 1:
                    current_row += 1
                elif key == ord('\n'):
                    return with_options[current_row]

                stdscr.refresh()

        result = curses.wrapper(menu)
        return result


class SliderMenu:
    @staticmethod
    def spawn(title: str, min_value: int = 0, max_value: int = 100, initial_value: int = 50,
              increment_level: int = 1) -> Optional[int]:
        def menu(stdscr):
            curses.curs_set(0)  # hide cursor
            stdscr.keypad(True)  # enable keypad mode
            curses.start_color()  # enable color
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

            current_value = initial_value
            while True:
                stdscr.clear()
                stdscr.addstr(0, 0, title, curses.color_pair(2))

                max_width = stdscr.getmaxyx()[1] - 12
                slider_position = int((current_value - min_value) / (max_value - min_value) * max_width)

                stdscr.addstr(2, 5, "[")
                stdscr.addstr(2, 6, " " * slider_position, curses.color_pair(1))
                stdscr.addstr(2, 6 + slider_position, " " * (max_width - slider_position))
                stdscr.addstr(2, 6 + max_width, "]")
                stdscr.addstr(4, 0, f"Value: {current_value}")

                stdscr.refresh()

                key = stdscr.getch()
                if key == curses.KEY_LEFT and current_value > min_value:
                    current_value = max(current_value - increment_level, min_value)
                elif key == curses.KEY_RIGHT and current_value < max_value:
                    current_value = min(current_value + increment_level, max_value)
                elif key == ord('\n'):
                    return current_value

        result = curses.wrapper(menu)
        return result
