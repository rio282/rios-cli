import curses
from typing import List, Optional, Any


class ListMenu:
    @staticmethod
    def spawn(with_options: List[str], title: Optional[str] = None, use_indexes: bool = True,
              quittable: bool = True) -> Optional[Any]:
        def menu(stdscr):
            stdscr.clear()

            curses.curs_set(0)  # hide cursor
            stdscr.keypad(True)  # enable keypad mode
            curses.start_color()  # enable color
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)

            nonlocal with_options
            max_y, max_x = stdscr.getmaxyx()
            view_height = max_y - 2  # view height excluding title and bottom padding
            start_idx = 0

            current_row = 0
            input_mode = False
            input_str = ""
            line_prompt_text = "Go to option (press 'Enter' to confirm, 'Esc' to cancel): "

            while True:
                stdscr.clear()

                if title:
                    stdscr.addstr(0, 0, title, curses.color_pair(2))

                # Calculate the end index for the viewable window
                end_idx = min(start_idx + view_height, len(with_options))

                # print menu options
                for index in range(start_idx, end_idx):
                    row = str(with_options[index])
                    row_str = f"[{index + 1}] {row[:max_x - 4]}" if use_indexes else f"{row[:max_x - 4]}"
                    if index == current_row:
                        stdscr.attron(curses.color_pair(1))
                        stdscr.addstr(index - start_idx + 1, 0, row_str)
                        stdscr.attroff(curses.color_pair(1))
                    else:
                        stdscr.addstr(index - start_idx + 1, 0, row_str)

                if input_mode:
                    stdscr.addstr(max_y - 1, 0, line_prompt_text)
                    stdscr.addstr(max_y - 1, len(line_prompt_text), input_str)
                else:
                    if quittable:
                        stdscr.addstr(max_y - 1, 0, " Press 'q' to quit, ':' to enter option number.")
                    else:
                        stdscr.addstr(max_y - 1, 0, " Press ':' to enter option number.")

                stdscr.refresh()

                # update selection
                key = stdscr.getch()

                if input_mode:
                    if key == curses.KEY_ENTER or key == 10:
                        try:
                            target_option = int(input_str) - 1
                            if 0 <= target_option < len(with_options):
                                current_row = target_option
                                start_idx = max(0, current_row - view_height + 1)
                        except ValueError:
                            pass
                        input_mode = False
                        input_str = ""
                        stdscr.clear()
                        continue
                    elif key == 27:  # Escape key
                        input_mode = False
                        input_str = ""
                        stdscr.clear()
                        continue
                    elif key == 8:  # win32 backspace key (doesn't make sense but ok)
                        input_str = input_str[:-1]
                    elif 32 <= key <= 126:
                        input_str += chr(key)
                else:
                    if key == curses.KEY_UP and current_row > 0:
                        current_row -= 1
                        if current_row < start_idx:
                            start_idx -= 1
                    elif key == curses.KEY_DOWN and current_row < len(with_options) - 1:
                        current_row += 1
                        if current_row >= end_idx:
                            start_idx += 1
                    elif key == ord(':'):
                        input_mode = True
                        input_str = ""
                    elif key == ord('q') and quittable:
                        return None
                    elif key == ord('\n'):
                        return with_options[current_row]

        if len(with_options) == 0:
            return None

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
