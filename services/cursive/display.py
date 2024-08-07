import pyaudio
import numpy as np
import curses
from typing import Optional, Final


class TextPane:
    @staticmethod
    def display(content: str, title: str = "", show_lines_in_title: bool = False) -> None:
        """Displays the given content in a scrollable pane using curses."""
        title = f"{title} ({content.count('\n') + 1} LINES)" if show_lines_in_title else title

        def inner(stdscr: curses.window) -> None:
            text_lines = content.splitlines()
            max_line_number = len(text_lines)
            max_line_number_width = len(str(max_line_number))
            max_width = len(max(text_lines, key=len))
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
                    percentage_x = int(current_col / max(max_width - max_x + 2, 1) * 100)
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

        curses.wrapper(inner)


class MusicVisualizer:
    def __init__(self, chunk=1024, rate=44100):
        self.CHUNK: Final[int] = chunk
        self.RATE: Final[int] = rate
        self.BUFFER_WAIT_TIME: Final[int] = 500
        self.REFRESH_DELAY: Final[int] = 66

        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.audio_buffer: np.ndarray = np.zeros((self.CHUNK,))
        self.running: bool = True

        # set up WASAPI loopback
        self.input_device_index = self.find_default_output_device()

    def find_default_output_device(self) -> int:
        devices = self.pyaudio_instance.get_device_info_by_index(0)
        default_device_index = None

        for i in range(self.pyaudio_instance.get_device_count()):
            device = self.pyaudio_instance.get_device_info_by_index(i)
            if device.get("defaultSampleRate") == self.RATE:
                default_device_index = i
                break

        if default_device_index is None:
            raise RuntimeError("Default output device not found or does not support the sample rate.")

        return default_device_index

    def get_audio_data(self, indata, frames, time, status):
        self.audio_buffer = np.copy(indata.flatten())

    def init_stream(self):
        try:
            self.stream = self.pyaudio_instance.open(format=pyaudio.paInt16,
                                                     channels=1,
                                                     rate=self.RATE,
                                                     input=True,
                                                     frames_per_buffer=self.CHUNK,
                                                     input_device_index=self.input_device_index,
                                                     stream_callback=self.get_audio_data,
                                                     as_loopback=True)  # enable WASAPI loopback
            self.stream.start_stream()
        except Exception as e:
            print(f"Error opening stream: {e}")

    def draw_bars(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(self.REFRESH_DELAY)

        height, width = stdscr.getmaxyx()

        while self.running:
            stdscr.clear()
            max_height = height - 1
            bar_width = max(1, width // self.CHUNK)

            audio_data = np.abs(self.audio_buffer)
            if np.max(audio_data) != 0:
                bars = (audio_data / np.max(audio_data) * max_height).astype(int)
            else:
                bars = np.zeros_like(audio_data, dtype=int)

            for i, bar_height in enumerate(bars):
                col_position = i * bar_width
                if col_position < width:
                    for j in range(bar_height):
                        try:
                            stdscr.addstr(max_height - j, col_position, '|')
                        except curses.error:
                            pass  # ignore if drawing outside the screen

            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('q'):
                self.running = False

    def start_visualization(self):
        self.init_stream()
        curses.wrapper(self.draw_bars)

    def close_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.pyaudio_instance.terminate()
