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
            max_line_number = len(text_lines)
            max_line_number_width = len(str(max_line_number))
            max_y, max_x = stdscr.getmaxyx()
            current_line = 0
            current_col = 0
            scroll_speeds = [1, 2, 4, 8]
            scroll_speed_index = 0
            show_line_numbers = False
            input_mode = False
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
                    if show_line_numbers:
                        line_number_str = f"{current_line + i + 1}"
                        line_number_str = line_number_str.rjust(max_line_number_width)
                        stdscr.addstr(
                            i,
                            0,
                            f"{line_number_str} | {line[current_col:current_col + max_x]}"
                        )
                    else:
                        stdscr.addstr(i, 0, line[current_col:current_col + max_x])

                # prepare strings
                if current_col == 0:
                    percentage_x = 0
                else:
                    percentage_x = int(current_col / max(len(text_lines[current_line]) - max_x + 1, 1) * 100)
                percentage_y = int(current_line / max(max_line_number - max_y + 1, 1) * 100)

                scroll_speed_str = f"Scroll Speed: {scroll_speeds[scroll_speed_index]}"
                percentage_str = f"{scroll_speed_str} | {percentage_x}% / {percentage_y}%".rjust(20)

                # bottom bar
                if not input_mode:
                    stdscr.hline(max_y - 1, 0, ' ', max_x, curses.color_pair(1))
                    stdscr.addstr(max_y - 1, 0, " Press 'q' to quit.", curses.color_pair(1))
                    stdscr.addstr(max_y - 1, max_x - len(percentage_str) - 1, percentage_str, curses.color_pair(1))
                    if title:
                        title_length = len(title)
                        start_x = (max_x - title_length) // 2
                        stdscr.addstr(max_y - 1, start_x, title, curses.color_pair(1))

                stdscr.refresh()

            def run() -> None:
                nonlocal current_line, current_col, scroll_speed_index, show_line_numbers, input_mode

                input_str = ""
                line_prompt_text = "Go to line (press 'Enter' to confirm, 'Esc' to cancel): "

                while True:
                    key = stdscr.getch()

                    if input_mode:
                        if key == curses.KEY_ENTER or key == 10:
                            try:
                                target_line = int(input_str) - 1
                                target_line = max(0, min(target_line, max_line_number - max_y + 1))
                                current_line = target_line
                                current_col = 0
                            except ValueError:
                                pass
                            input_mode = False
                            input_str = ""
                            stdscr.clear()
                            draw_pane()
                            continue
                        elif key == 27:  # Escape key
                            input_mode = False
                            input_str = ""
                            stdscr.clear()
                            draw_pane()
                            continue
                        elif key == 8:  # win32 backspace key (doesn't make sense but ok)
                            input_str = input_str[:-1]
                            stdscr.hline(max_y - 1, 0, ' ', max_x)  # clear row to delete trailing characters
                        elif 32 <= key <= 126:
                            input_str += chr(key)

                        draw_pane()
                        stdscr.addstr(max_y - 1, 0, line_prompt_text)
                        stdscr.addstr(max_y - 1, len(line_prompt_text), input_str)
                        stdscr.refresh()

                    else:
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
                        elif key == ord('l'):
                            show_line_numbers = not show_line_numbers
                            stdscr.clear()
                            draw_pane()
                        elif key == ord(':'):
                            input_mode = True
                            stdscr.clear()
                            draw_pane()
                            stdscr.addstr(max_y - 1, 0, line_prompt_text)
                            stdscr.refresh()
                        elif key == ord('q'):
                            break

                curses.endwin()

            def scroll_up() -> None:
                nonlocal current_line
                if current_line > 0:
                    current_line = max(0, current_line - scroll_speeds[scroll_speed_index])
                    draw_pane()

            def scroll_down() -> None:
                nonlocal current_line
                if current_line < max_line_number - max_y + 1:
                    current_line = min(max_line_number - max_y + 1, current_line + scroll_speeds[scroll_speed_index])
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
