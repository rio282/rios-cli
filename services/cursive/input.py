import curses
from typing import Optional


class InputMenu:
    @staticmethod
    def spawn(input_text: str, title: Optional[str] = None) -> Optional[str]:
        def menu(stdscr):
            curses.curs_set(0)
            stdscr.keypad(True)
            curses.start_color()

            _, max_x = stdscr.getmaxyx()
            curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

            user_input = ""
            while True:
                stdscr.clear()

                if title:
                    stdscr.addstr(0, 0, title, curses.color_pair(1))
                stdscr.addstr(1, 0, input_text + user_input)

                stdscr.refresh()

                key = stdscr.getch()
                if key == curses.KEY_ENTER or key == 10:
                    return user_input
                elif key == 8 or key == curses.KEY_BACKSPACE:
                    user_input = user_input[:-1]
                    stdscr.hline(1, 0, ' ', max_x)
                elif 32 <= key <= 126:
                    user_input += chr(key)

        result = curses.wrapper(menu)
        return result
