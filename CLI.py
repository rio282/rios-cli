import cmd
import os
import sys
import shutil
import webbrowser

import win32gui, win32con
from psutil._common import bytes2human

from colorama import init, Fore
from pprint import pprint

from etc.utils import truncate_filename, AutoCompletion, is_integer
from etc.pepes import *
from services import youtube, file_system, network, com, processes, statistics, web_searcher, local_searcher
from services.cursive import InteractiveMenu, SliderMenu, ScrollableTextPane
from typing import Final, List, Tuple
from playsound import playsound
from datetime import date, datetime

from services.osys import AudioService
from services.search.web import WebSearchResult

intro_logo: Final[str] = Fore.GREEN + r"""
                                                      ⠀⠀       ⠀⠀⠀  ⣀⣤⡤⠀⠀⠀
                                                      ⠀⠀       ⠀⠀ ⢀⣾⣿⠋⠀
                                                      ⠀⠀⠀       ⠀⣠⣾⣿⡟⠀⠀
ooooooooo.             .oooooo.   ooooo        ooooo ⠀         ⠀⢸⠛⠉⢹⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠄⠠⣀⠀⠀⠀⠀⠀⠀⠀
`888   `Y88.          d8P'  `Y8b  `888'        `888' ⠀⠀         ⡘⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠖⠉⠀⠀⠀⣾⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀
 888   .d88'         888           888          888 ⠀          ⠀⡇⠀⠀⠀⢡⠄⠀⠀⣀⣀⣀⣠⠊⠀⠀⠀⠀⡠⠞⠛⠛⠛⠛⠀⠀⠀
 888ooo88P'          888           888          888   ⠀        ⠀⢃⠀⠀⠀⠀⠗⠚⠉⠉⠀⠈⠁⠀⠀⠀⢀⡔⠁⠀
 888`88b.    8888888 888           888          888          ⠀ ⠀⠸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣶⣄⠲⡎⠀⠀
 888  `88b.          `88b    ooo   888       o  888   ⠀      ⠀  ⠀⠃⠀⠀⢠⣤⡀⠀⠀⠀⠀⣿⣿⣿⠀⠘⡄
o888o  o888o          `Y8bood8P'  o888ooooood8 o888o⠀⠀          ⠀⡆⠀⠀⣿⣿⡇⠀⠀⠀⠀⠈⠛⠉⣴⣆⢹⡄⠀⠀
                                                      ⠀        ⠀⠀⣇⢰⡧⣉⡉⠀⠀⢀⡀⠀⣀⣀⣠⣿⡷⢠⡇⠀⠀⠀
                                                                 ⢻⠘⠃⠈⠻⢦⠞⠋⠙⠺⠋⠉⠉⠉⢡⠟⠀⠀⠀⠀
                                                                 ⠀⠳⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠋⠀            
""" + Fore.RESET


class RiosCLI(cmd.Cmd):
    prompt: str = Fore.WHITE + "~$ "
    intro: Final[str] = f"{intro_logo}\nHello master, what can I do for you?"

    def __init__(self):
        super().__init__()

        # init stuff
        init(autoreset=True)

        # cli setup
        self.__is_windows: Final[bool] = os.name == "nt"
        self.clear_command: Final[str] = "cls" if self.__is_windows else "clear"

        # paths
        self.script_wd: Final[str] = os.path.dirname(os.path.abspath(__file__))
        os.chdir(os.path.expanduser("~/Desktop"))
        self.current_directory: str = os.getcwd()

        # windows full screen
        if self.__is_windows:
            self.hwnd = win32gui.GetForegroundWindow()
            self.__set_fullscreen()

        os.system(f"title Rio's CLI -- {date.today()}")

    def __change_prompt_prefix_to(self, prefix: str = ""):
        users_directory = "C:\\Users\\"
        user_home_directory = os.path.abspath(os.path.expanduser("~/Desktop"))

        if prefix == user_home_directory:
            prefix = ""
        elif prefix.startswith(users_directory):
            prefix = prefix.replace(users_directory, "u:")

        if prefix != "":
            prefix += " "

        self.prompt = f"{Fore.WHITE}{prefix}~$ "

    def __on_error(self, error_exception: Exception):
        print(f"{Fore.RED}[!] An error has occurred: {error_exception}")

    def __set_fullscreen(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)

    def __minimize_window(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)

    def list_files(self, files: List[Tuple[str, float]]):
        print()
        print(f"{Fore.GREEN}Files:")
        formatted_file_info = []
        max_length = 32
        for file in files:
            file, file_size = file
            filename, file_ext = os.path.splitext(file)

            padding_length = max_length - len(filename) - len(file_ext)
            file_size_mb_rounded = float(f"{file_size:.2f}")

            f_filename = truncate_filename(filename, file_ext, max_length)
            f_file_size = f"{Fore.CYAN}{file_size_mb_rounded} MB" if file_size_mb_rounded > 0 else f"{Fore.CYAN}~{file_size_mb_rounded} MB"
            filename_padding = f"{Fore.LIGHTBLACK_EX}{'-' * padding_length}{Fore.RESET}"

            formatted_file_info.append(f"{f_filename}{filename_padding} | {f_file_size}")

        print(*formatted_file_info, sep="\n")

    def list_directories(self, directories: List[str]):
        print()
        print(f"{Fore.GREEN}Directories:")
        print(*[f"{Fore.LIGHTBLACK_EX}{directory}" if directory.startswith(".") else directory for directory in
                directories], sep="\n")

    def postcmd(self, stop, line):
        if line.strip() != "":
            print()  # add empty line for better readability
        return stop

    def preloop(self):
        file_system.load_cache()
        web_searcher.load_cache()

    def postloop(self):
        file_system.save_cache()
        web_searcher.save_cache()

    def emptyline(self):
        pass

    def do_hello(self, line):
        """Replies with Hi!"""
        print("Hi!")

    def do_hi(self, line):
        """Replies with Hello!"""
        print("Hello!")

    def do_ping(self, line):
        """Replies with Pong!"""
        print("Pong!")

    def do_cd(self, directory):
        """Change current directory."""
        if not directory:
            print(self.current_directory)
            return

        if directory == ".":
            print(f"Changed directory to {self.current_directory}")
            return
        elif directory == "..":
            directory = os.path.dirname(self.current_directory)

        new_dir = file_system.clean_directory(directory)
        if os.path.exists(new_dir) and os.path.isdir(new_dir):
            self.current_directory = new_dir
            os.chdir(self.current_directory)
            print(f"Changed directory to {self.current_directory}")
            self.__change_prompt_prefix_to(new_dir)
        else:
            print(f"Directory '{directory}' does not exist.")

    def complete_cd(self, text, line, begidx, endidx):
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx,
                                                AutoCompletion.DIRECTORIES)

    def do_ls(self, directory):
        """Lists the files and directories in a directory."""
        try:
            if directory == "--inspect-cache":
                file_cache = file_system.file_cache
                dir_cache = file_system.directory_cache

                print(f"{Fore.GREEN}Directory cache:")
                pprint(dir_cache if dir_cache else "Empty.")
                print()
                print(f"{Fore.GREEN}File cache:")
                pprint(file_cache if file_cache else "Empty.")
                return

            print_dirs = False
            print_files = False
            use_cache = "--use-cache" in directory

            if "--dirs" in directory:
                print_dirs = True
            if "--files" in directory:
                print_files = True
            if not print_dirs and not print_files:
                print_dirs = True
                print_files = True

            if print_dirs:
                directories = file_system.get_directories_in_directory(directory, use_cache)
                self.list_directories(directories)
            if print_files:
                files = file_system.get_files_in_directory(directory, use_cache)
                self.list_files(files)
        except Exception as e:
            self.__on_error(e)

    def complete_ls(self, text, line, begidx, endidx):
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx,
                                                AutoCompletion.DIRECTORIES)

    def do_open(self, filename):
        """Opens a file in the specified path."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            os.startfile(file_path)
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"Error trying to open file: {e}")

    def complete_open(self, text, line, begidx, endidx):
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx)

    def do_create(self, filename):
        """Create a new file in the current directory."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            if os.path.exists(file_path):
                print(f"Directory '{file_path}' already exists in directory '{file_path.removesuffix(filename)}'")
            else:
                with open(file_path, "w"):
                    print(f"File '{filename}' created in {self.current_directory}")
        except Exception as e:
            self.__on_error(e)

    def do_mkdir(self, directory_name):
        """Create a new directory in the current directory."""
        directory_path = os.path.join(self.current_directory, directory_name)
        if os.path.exists(directory_path):
            directory_path = directory_path.removesuffix(directory_name)
            print(f"Directory '{directory_name}' already exists in directory '{directory_path}'")
            return

        os.mkdir(directory_path)
        print(f"Created directory at: {directory_path}")

    def do_read(self, filename):
        """Read the contents of a text file in the current directory."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            with open(file_path, "r") as existing_file:
                content = existing_file.read()

            ScrollableTextPane.display(content, title=filename)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{filename}' not found.")
        except Exception as e:
            self.__on_error(e)

    def complete_read(self, text, line, begidx, endidx):
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx,
                                                AutoCompletion.FILES)

    def do_rm(self, filename):
        """Removes a file or directory."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            if not os.path.exists(file_path):
                print(f"File '{filename}' not found.")
                return

            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)

            print(f"Removed: {file_path}")
        except PermissionError as e:
            self.__on_error(e)

    def complete_rm(self, text, line, begidx, endidx):
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx)

    def do_zip(self, directory):
        """Zips a directory. (Subcommands available)"""
        try:
            if "--ls" in directory:
                directory = directory.replace("--ls", "").strip()
                zip_content = file_system.view_zip_content(directory)
                self.list_directories(zip_content.get("directories"))
                self.list_files(zip_content.get("files"))
                return

            file_system.zip(directory)
            print(Fore.GREEN + f"Zipped: {directory}")
        except Exception as e:
            self.__on_error(e)

    def complete_zip(self, text, line, begidx, endidx):
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx)

    def do_unzip(self, zip_file):
        """Unzips a directory."""
        try:
            file_system.unzip(zip_file)
            print(Fore.GREEN + f"Unzipped: {zip_file}")
        except Exception as e:
            self.__on_error(e)

    def complete_unzip(self, text, line, begidx, endidx):
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx,
                                                AutoCompletion.FILES)

    def do_fart(self, line):
        """Plays fart sound."""
        print(f"{cool_pepe}\nThppt! *Shits pants*")
        fart_sound_wav = os.path.join(self.script_wd, "res", "fart.wav")
        playsound(fart_sound_wav)

    def do_youtube(self, video_url):
        """Parses YouTube command(s)."""
        result = InteractiveMenu.spawn(["Video + Audio", "Audio only", "Exit"]).lower()
        if result == "exit":
            return

        audio_only = result == "audio only"
        success = youtube.downloader.download(video_url, audio_only)

        if success:
            print(f"\n{Fore.GREEN}Download completed!")
        else:
            print(f"\n{Fore.GREEN}Something went wrong.")

    def do_now(self, line):
        """Shows current date (along with day of week) and time."""
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime("%Y-%m-%d")
        formatted_time = current_datetime.strftime("%H:%M:%S")
        formatted_day = current_datetime.strftime("%A")
        print(f"Today is {formatted_day} {formatted_date} and it's currently {formatted_time}.")

    def do_downloads(self, line):
        """Opens downloads folder."""
        self.do_open(os.path.expanduser("~/Downloads"))

    def do_music(self, line):
        """Opens music folder."""
        print(music_pepe)
        self.do_open(os.path.expanduser("~/Music"))

    def do_videos(self, line):
        """Opens videos folder."""
        self.do_open(os.path.expanduser("~/Videos"))

    def do_volume(self, line):
        """Adjusts volume for windows."""
        if not line:
            new_volume_level = SliderMenu.spawn("Volume", increment_level=2, initial_value=AudioService.get_volume())
        else:
            if not is_integer(line) or not 0 < int(line) < 100:
                print(f"{Fore.RED}Value must be a number between 0-100.")
                return
            new_volume_level = line

        try:
            new_volume_level = int(new_volume_level)
            AudioService.set_volume_to(new_volume_level)
        except Exception as e:
            self.__on_error(e)

    def do_procs(self, subcommands):
        """Allows you to interact with certain processes."""
        subcommands = subcommands.split()
        if not subcommands:
            processes.list_processes()
            return

        command = subcommands[0].lower()
        command_args = subcommands[1:]
        command_methods = {
            "list": processes.list_processes,
            "kill": processes.kill_process
        }

        if command in command_methods:
            command_methods[command](*command_args)
            return

        self.default(subcommands)

    def do_ustats(self, line):
        """Usage statistics."""
        stats = statistics.all
        align_length = 20

        cpu_usage = f"{stats['cpu_percent']:.1f}%"
        memory_usage = f"{stats['memory_info'].percent:.1f}%"
        disk_usage = f"{stats['disk_usage'].percent:.1f}%"

        memory_used = f"{bytes2human(stats['memory_info'].used)} / {bytes2human(stats['memory_info'].total)}"
        memory_free = f"{bytes2human(stats['memory_info'].free)}"

        disk_used = f"{bytes2human(stats['disk_usage'].used)} / {bytes2human(stats['disk_usage'].total)}"
        disk_free = f"{bytes2human(stats['disk_usage'].free)}"

        print()
        print(
            Fore.WHITE +
            f"{''.ljust(8)} {'CPU'.ljust(align_length)} {'Memory'.ljust(align_length)} {'Disk'.ljust(align_length)}"
        )
        print(
            Fore.WHITE +
            f"{'Usage:'.rjust(8)}{Fore.RESET} {cpu_usage.ljust(align_length)} {memory_usage.ljust(align_length)} {disk_usage.ljust(align_length)}"
        )
        print(
            Fore.WHITE +
            f"{'Used:'.rjust(8)}{Fore.RESET} {''.ljust(align_length)} {memory_used.ljust(align_length)} {disk_used.ljust(align_length)}"
        )
        print(
            Fore.WHITE +
            f"{'Free:'.rjust(8)}{Fore.RESET} {''.ljust(align_length)} {memory_free.ljust(align_length)} {disk_free.ljust(align_length)}"
        )

    def do_net(self, subcommands):
        """Extensive information about the network when used correctly."""
        try:
            subcommands = subcommands.split()
            subcommand = subcommands.pop(0) if len(subcommands) > 0 else None

            if subcommand == "keys":
                ssid_password = network.get_ssid_password()
                print(Fore.GREEN + ssid_password)
            else:
                print(Fore.RED + "Unknown subcommand specified.")
        except Exception as e:
            self.__on_error(e)

    def do_com(self, line):
        """Allows interaction with COM port(s)."""
        subcommand = InteractiveMenu.spawn(["Scan", "Exit"]).lower()

        if subcommand == "exit":
            return

        if subcommand == "scan":
            connections = com.connections
            print(f"{Fore.GREEN}Connections:")
            if connections:
                print(*connections)
            else:
                print("No connections to COM port(s).")
        else:
            self.default(subcommand)

    def do_search(self, query):
        """Searches a specified place for something to match the given query."""
        query = query.strip()
        search_type = InteractiveMenu.spawn(["Web", "Locally", "Exit"], "Where do you want to search?").lower()

        if search_type == "locally":
            print(f"{Fore.LIGHTBLACK_EX}Searching locally for: '{query}'...")
            results = local_searcher.search(query)
        elif search_type == "web":
            print(f"{Fore.LIGHTBLACK_EX}Searching the web for: '{query}'...")
            results = web_searcher.search(query)
        elif search_type == "exit":
            return
        else:
            self.default(query)
            return

        # create a copy of the results list and add "== Exit ==" to it
        exit_text = ">>> Exit"
        results_with_exit = results.copy()
        results_with_exit.append(WebSearchResult(exit_text, ""))

        result = InteractiveMenu.spawn([r.title for r in results_with_exit], f"Search results ({len(results)})")
        selected_result = next((r for r in results_with_exit if r.title == result), None)
        if selected_result.title == exit_text:
            return

        webbrowser.open(selected_result.href, new=0, autoraise=True)

    def do_hide(self, line):
        """Hides (minimizes) console window."""
        if self.__is_windows:
            print(Fore.RESET + "Sshh!")
            print(Fore.RESET + "(Cya soon!)")
            self.__minimize_window()
        else:
            print(f"{Fore.RED}Windows support only.")

    def do_clear(self, line):
        """Clears screen."""
        os.system(self.clear_command)
        print(self.intro)

    def do_q(self, line):
        """Exit CLI."""
        return True

    def do_reload(self, line):
        """Reloads/Restarts the CLI."""
        print("Running postloop...")
        self.postloop()

        print("Reloading...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
