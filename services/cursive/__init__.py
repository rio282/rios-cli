import curses
from abc import ABC
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


class ScrollableTextPane:
    @staticmethod
    def display(content: str, title: str = "") -> None:
        """Displays the given content in a scrollable pane using curses."""

        def __display(stdscr: curses.window) -> None:
            text_lines = content.splitlines()
            max_y, max_x = stdscr.getmaxyx()
            current_line = 0
            current_col = 0
            scroll_speeds = [1, 2, 4, 8]
            scroll_speed_index = 0
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

            def initialize_screen() -> None:
                curses.curs_set(0)  # hide cursor
                stdscr.clear()
                draw_pane()
                run()

            def draw_pane() -> None:
                stdscr.clear()

                # print content
                for i, line in enumerate(text_lines[current_line:current_line + max_y - 1]):
                    stdscr.addstr(i, 0, line[current_col:current_col + max_x])

                # prepare strings
                if current_col == 0:
                    percentage_x = 0
                else:
                    percentage_x = int(current_col / max(len(text_lines[current_line]) - max_x + 1, 1) * 100)
                percentage_y = int(current_line / max(len(text_lines) - max_y + 1, 1) * 100)

                scroll_speed_str = f"Scroll Speed: {scroll_speeds[scroll_speed_index]}"
                percentage_str = f"{scroll_speed_str} | {percentage_x}% / {percentage_y}%".rjust(20)

                # bottom bar
                stdscr.hline(max_y - 1, 0, ' ', max_x, curses.color_pair(1))
                stdscr.addstr(max_y - 1, 0, "Press 'q' to quit.", curses.color_pair(1))
                stdscr.addstr(max_y - 1, max_x - len(percentage_str) - 1, percentage_str, curses.color_pair(1))
                if title:
                    title_length = len(title)
                    start_x = (max_x - title_length) // 2
                    stdscr.addstr(max_y - 1, start_x, title, curses.color_pair(1))

                stdscr.refresh()

            def run() -> None:
                nonlocal current_line, current_col, scroll_speed_index
                while True:
                    key = stdscr.getch()
                    if key == curses.KEY_UP:
                        scroll_up()
                    elif key == curses.KEY_DOWN:
                        scroll_down()
                    elif key == curses.KEY_LEFT:
                        scroll_left()
                    elif key == curses.KEY_RIGHT:
                        scroll_right()
                    elif key == ord(' '):
                        scroll_speed_index = (scroll_speed_index + 1) % len(scroll_speeds)
                        draw_pane()
                    elif key == ord('q'):
                        break

            def scroll_up() -> None:
                nonlocal current_line
                if current_line > 0:
                    current_line = max(0, current_line - scroll_speeds[scroll_speed_index])
                    draw_pane()

            def scroll_down() -> None:
                nonlocal current_line
                if current_line < len(text_lines) - max_y + 1:
                    current_line = min(len(text_lines) - max_y + 1, current_line + scroll_speeds[scroll_speed_index])
                    draw_pane()

            def scroll_left() -> None:
                nonlocal current_col
                if current_col > 0:
                    current_col = max(0, current_col - scroll_speeds[scroll_speed_index])
                    draw_pane()

            def scroll_right() -> None:
                nonlocal current_col
                if current_col < max(len(line) for line in text_lines) - max_x:
                    current_col = min(max(len(line) for line in text_lines) - max_x,
                                      current_col + scroll_speeds[scroll_speed_index])
                    draw_pane()

            initialize_screen()

        curses.wrapper(__display)
