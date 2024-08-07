import pyaudio
import numpy as np
import curses
from typing import Optional, Final


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
