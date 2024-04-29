import cmd
import os

from colorama import init, Fore, Back

import youtube
import shutil
from typing import Final
from playsound import playsound

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
        self.original_cwd: Final[str] = os.getcwd()

        self.clear_command = "cls" if os.name == "nt" else "clear"
        os.chdir(os.path.expanduser("~/Desktop"))
        self.current_directory: str = os.getcwd()

    def postcmd(self, stop, line):
        print()  # add empty line for better readability
        return stop

    def do_hello(self, line):
        print("Hi!")

    def do_ping(self, line):
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
            self.current_directory = new_dir
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
        print(f"{Fore.RED}Directories:")
        print(*[f"{Fore.LIGHTBLACK_EX}{directory}" if directory.startswith(".") else directory
                for directory in directories], sep="\n")

        print()

        # print out files
        print(f"{Fore.RED}Files:")
        formatted_file_info = []
        for file in files:
            filename, file_ext = os.path.splitext(file)
            f_filename = f"{filename}{Fore.LIGHTBLACK_EX}{file_ext}"
            try:
                file_size = os.stat(f"{filename}{file_ext}").st_size / (1024 * 1024)
                file_size_rounded = float(f"{file_size:.2f}")

                f_file_size = f"{Fore.CYAN}{file_size_rounded}MB" if file_size_rounded > 0 else f"{Fore.CYAN}~{file_size_rounded}MB"
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
        line = line.split(" ")
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

    def do_yt(self, line):
        """Alias for YouTube."""
        self.do_youtube(line)

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
