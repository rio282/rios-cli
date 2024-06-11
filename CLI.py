import cmd
import os
import psutil
import win32gui, win32con

from colorama import init, Fore, Back

import youtube
import shutil
from typing import Final
from playsound import playsound
from datetime import date, datetime

from etc import network, music_player

intro_logo: Final[str] = Fore.GREEN + r"""
  o__ __o          o                   o/                      o__ __o     o           __o__ 
 <|     v\       _<|>_                /v                      /v     v\   <|>            |   
 / \     <\                          />                      />       <\  / \           / \  
 \o/     o/        o      o__ __o              __o__       o/             \o/           \o/  
  |__  _<|        <|>    /v     v\            />  \       <|               |             |   
  |       \       / \   />       <\           \o           \\             / \           < >  
 <o>       \o     \o/   \         /            v\            \         /  \o/            |   
  |         v\     |     o       o              <\            o       o    |             o   
 / \         <\   / \    <\__ __/>         _\o__</            <\__ __/>   / \ _\o__/_  __|>_ 
""" + Fore.RESET


class RiosCLI(cmd.Cmd):
    prompt: Final[str] = Fore.WHITE + "~$ "
    intro: Final[str] = f"{intro_logo}\nHello master, what can I do for you?"

    def __init__(self):
        super().__init__()

        # init stuff
        init(autoreset=True)

        # cli setup
        self.__is_windows: Final[bool] = os.name == "nt"
        self.clear_command: Final[str] = "cls" if self.__is_windows else "clear"

        # paths
        self.original_cwd: Final[str] = os.getcwd()
        os.chdir(os.path.expanduser("~/Desktop"))
        self.current_directory: str = os.getcwd()

        # windows full screen
        if self.__is_windows:
            self.hwnd = win32gui.GetForegroundWindow()
            self.__set_fullscreen()

        os.system(f"title Rio's CLI -- {date.today()}")

    def __set_fullscreen(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MAXIMIZE)

    def __minimize_window(self):
        win32gui.ShowWindow(self.hwnd, win32con.SW_MINIMIZE)

    def postcmd(self, stop, line):
        if line.strip() != "":
            print()  # add empty line for better readability
        return stop

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

        if directory == "..":
            self.current_directory = os.path.dirname(self.current_directory)
            print(f"Changed directory to {self.current_directory}")
            return

        new_dir = os.path.join(self.current_directory, directory)
        if os.path.exists(new_dir) and os.path.isdir(new_dir):
            self.current_directory = os.path.join(self.current_directory, os.path.basename(new_dir))
            os.chdir(self.current_directory)
            print(f"Changed directory to {self.current_directory}")
        else:
            print(f"Directory '{directory}' does not exist.")

    def do_ls(self, directory):
        """Lists the files and directories in a directory."""
        files = []
        directories = []

        if directory and not os.path.exists(directory):
            print(f"Directory '{directory}' doesn't exist.")
            return

        cd = self.current_directory if not directory else directory.replace(":", ":\\")  # to fix weird bug
        for entry in os.listdir(cd):
            if os.path.isfile(os.path.join(cd, entry)):
                files.append(entry)
            elif os.path.isdir(os.path.join(cd, entry)):
                directories.append(entry)

        # print out dirs
        print(f"{Fore.GREEN}Directories:")
        print(*[f"{Fore.LIGHTBLACK_EX}{directory}" if directory.startswith(".") else directory
                for directory in directories], sep="\n")

        print()

        # print out files
        print(f"{Fore.GREEN}Files:")
        formatted_file_info = []
        for file in files:
            filename, file_ext = os.path.splitext(file)
            f_filename = f"{filename}{Fore.LIGHTBLACK_EX}{file_ext}"
            try:
                file_size_mb = os.stat(f"{filename}{file_ext}").st_size / (1024 * 1024)
                file_size_mb_rounded = float(f"{file_size_mb:.2f}")

                f_file_size = f"{Fore.CYAN}{file_size_mb_rounded}MB" if file_size_mb_rounded > 0 else f"{Fore.CYAN}~{file_size_mb_rounded}MB"
                formatted_file_info.append(f"{f_filename} {f_file_size}")
            except FileNotFoundError:
                formatted_file_info.append(f"{f_filename} {Fore.CYAN}__.__MB")

        print(*formatted_file_info, sep="\n")

    def do_open(self, filename):
        """Opens a file in the specified path."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            os.startfile(file_path)
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"Error trying to open file: {e}")

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
            print("An unknown error occurred:", e)

    def do_createf(self, directory_name):
        """Create a new directory in the current directory."""
        directory_path = os.path.join(self.current_directory, directory_name)
        if os.path.exists(directory_path):
            print(
                f"Directory '{directory_name}' already exists in directory '{directory_path.removesuffix(directory_name)}'")
        else:
            os.mkdir(directory_path)
            print(f"Created directory at: {directory_path}")

    def do_created(self, directory_name):
        """Alias for createf (create folder)."""
        self.do_createf(directory_name)

    def do_mkdir(self, directory_name):
        """Alias for createf."""
        self.do_created(directory_name)

    def do_check(self, filename):
        """Read the contents of a text file in the current directory."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            with open(file_path, "r") as existing_file:
                print(existing_file.read())
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"Error trying to read file: {e}")

    def do_remove(self, filename):
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
        except PermissionError:
            print("Access denied.")

    def do_fart(self, line):
        """Plays fart sound."""
        print("Thppt! *Shits pants*")
        fart_sound_wav = os.path.join(self.original_cwd, "res", "fart.wav")
        playsound(fart_sound_wav)

    def do_youtube(self, line):
        """Parses YouTube command(s)."""
        line = line.split()
        video_url = line[0]
        audio_only = False

        if len(line) > 2:
            print("Invalid use of command.")
            return
        elif len(line) == 2 and line.pop() == "audio":
            audio_only = True

        success = youtube.downloader.download(video_url, audio_only)
        print()
        if success:
            print(Fore.GREEN + "Download completed!")
        else:
            print(Fore.RED + "Something went wrong.")

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
        self.do_open(os.path.expanduser("~/Music"))

    def do_videos(self, line):
        """Opens videos folder."""
        self.do_open(os.path.expanduser("~/Videos"))

    def do_play(self, filename):
        """Plays video in preferred program OR plays audio in the background."""
        file_path = os.path.join(self.current_directory, filename)
        if os.path.isdir(file_path):
            raise NotImplemented

        video_extensions = ["mp4", "mkv", "avi", "mov", "wmv", "flv", "webm"]
        audio_extensions = ["mp3", "wav", "flac", "aac", "ogg", "wma", "m4a", "aiff", "ape"]

        try:
            file_extension = os.path.splitext(file_path)[1].removeprefix(".").lower()
            if file_extension in video_extensions:
                self.do_open(file_path)
            elif file_extension in audio_extensions:
                music_player.play(file_path)
            else:
                print(Fore.RED + "Unrecognized video/audio format.")
        except FileNotFoundError:
            print(f"File '{filename}' not found.")
        except Exception as e:
            print(f"Error trying to open file: {e}")

    def do_volume(self, line):
        """Adjusts volume for windows or built-in music player."""
        raise NotImplemented

    def do_programs(self, subcommands):
        """Allows you to interact with certain processes."""
        subcommands = subcommands.split()
        if not subcommands or subcommands[0] == "list":
            running_processes = [process for process in psutil.process_iter() if process.is_running()]
            running_processes.sort(key=lambda process: process.name())

            for process in running_processes:
                print(f"{Fore.LIGHTBLACK_EX}{process.pid:<5} {Fore.RESET}{process.name()}")

        elif subcommands[0] == "kill":
            if len(subcommands) != 2:
                print(Fore.RED + "Invalid use of command.")
                return

            prgm_to_kill = subcommands[1]
            killed = False
            for process in psutil.process_iter():
                if process.name().lower() == prgm_to_kill.lower():
                    process.kill()
                    print(f"{Fore.GREEN}Killed {process.name()} ({process.pid})")
                    killed = True

            if not killed:
                print(f"{Fore.RED}Couldn't find program '{prgm_to_kill}'.")
        else:
            self.default(subcommands)

    def do_prgms(self, line):
        """Alias for programs."""
        self.do_programs(line)

    def do_network(self, subcommands):
        """Extensive information about the network when used correctly."""
        subcommands = subcommands.split()
        subcommand = subcommands.pop(0) if len(subcommands) > 0 else None

        if network_init_failed:
            print(Fore.RED + "Network initialization failed. Are you sure you installed everything correctly?")
            return

        if subcommand == "keys":
            ssid_password = network.get_ssid_password()
            print(Fore.GREEN + ssid_password)
        else:
            print(Fore.RED + "Unknown subcommand specified.")

    def do_net(self, line):
        """Alias for network."""
        self.do_network(line)

    def do_yt(self, line):
        """Alias for YouTube."""
        self.do_youtube(line)

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

    def do_cls(self, line):
        """Alias for clear."""
        self.do_clear(line)

    def do_quit(self, line):
        """Exit CLI."""
        return True

    def do_exit(self, line):
        """Alias for exit."""
        return self.do_quit(line)

    def do_q(self, line):
        """Alias for quit."""
        return self.do_exit(line)
