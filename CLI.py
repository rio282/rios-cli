import cmd
import json
import os
import random
import shutil
import sys
import webbrowser
from datetime import date, datetime
from pprint import pprint
from time import sleep
from typing import Final, List, Tuple

from colorama import init, Fore
from playsound import playsound
from psutil._common import bytes2human

from etc.pepes import *
from etc.utils import truncate_filename, AutoCompletion, is_integer
from games.horse_racing import HorseRace
from services import youtube, anime, file_system, com, processes, statistics, web_searcher, local_searcher, \
    history_manager, cache_directory
from services.cursive import ListMenu, SliderMenu, TextPane
from services.cursive.editors import InputMenu
from services.cursive.music import MusicVisualizer
from services.internal.config import Config
from services.music import MusicPlayer, music_player
from services.osys import AudioService
from services.search import SearchResultEncoder

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
    nohelp: str = f"%s? What's that? -- I wonder who forgot to write documentation about this command... {Fore.WHITE}*ahem*{Fore.RESET}"
    intro: Final[str] = f"{intro_logo}\nHello master, what can I do for you?"

    def __init__(self):
        super().__init__()

        # init stuff
        init(autoreset=True)

        # cli setup
        self.clear_command: Final[str] = "cls"

        # paths
        self.script_wd: Final[str] = os.path.dirname(os.path.abspath(__file__))
        os.chdir(os.path.expanduser("~/Desktop"))
        self.current_directory: str = os.getcwd()

        # load config
        config_dir = os.path.join(self.script_wd, ".config")
        self.config = Config(config_dir)
        if not os.path.exists(self.config.config_file):
            self.config.create_default_config()

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
            history_manager.record_line(line)

        return stop

    def preloop(self):
        file_system.load()
        local_searcher.load()
        web_searcher.load()
        history_manager.load()

    def postloop(self):
        file_system.save()
        local_searcher.save()
        web_searcher.save()
        history_manager.save()

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
        return AutoCompletion.path(self.current_directory, text, line, begidx, endidx,
                                   AutoCompletion.TYPE_DIRECTORIES)

    def do_ls(self, directory):
        """Lists the files and directories in a directory."""
        try:
            directory = directory.strip()

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

            if os.path.isfile(directory) and os.path.splitext(directory)[1] == ".zip":
                # zip files
                zip_content = file_system.get_zip_content(directory)
                if print_dirs:
                    self.list_directories(zip_content.get("directories"))
                if print_files:
                    self.list_files(zip_content.get("files"))
            else:
                # normal directories
                if print_dirs:
                    directories = file_system.get_directories_in_directory(directory, use_cache)
                    self.list_directories(directories)
                if print_files:
                    files = file_system.get_files_in_directory(directory, use_cache)
                    self.list_files(files)
        except Exception as e:
            self.__on_error(e)

    def complete_ls(self, text, line, begidx, endidx):
        return AutoCompletion.path(self.current_directory, text, line, begidx, endidx,
                                   AutoCompletion.TYPE_DIRECTORIES_AND_ZIP)

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
        return AutoCompletion.path(self.current_directory, text, line, begidx, endidx)

    def do_create(self, filename, silent=False):
        """Create a new file in the current directory."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            if os.path.exists(file_path):
                if not silent:
                    print(f"Directory '{file_path}' already exists in directory '{file_path.removesuffix(filename)}'")
            else:
                with open(file_path, "w"):
                    if not silent:
                        print(f"File '{filename}' created in {self.current_directory}")
        except Exception as e:
            self.__on_error(e)

    def do_mkdir(self, directory_name, silent: bool = False):
        """Create a new directory in the current directory."""
        directory_path = os.path.join(self.current_directory, directory_name)
        if os.path.exists(directory_path):
            directory_path = directory_path.removesuffix(directory_name)
            if not silent:
                print(f"Directory '{directory_name}' already exists in directory '{directory_path}'")
            return

        os.mkdir(directory_path)
        if not silent:
            print(f"Created directory at: {directory_path}")

    def do_read(self, filename):
        """Read the contents of a text file in the current directory."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            with open(file_path, "r") as existing_file:
                content = existing_file.read()

            TextPane.display(content, title=filename)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{filename}' not found.")
        except Exception as e:
            self.__on_error(e)

    def complete_read(self, text, line, begidx, endidx):
        return AutoCompletion.path(self.current_directory, text, line, begidx, endidx,
                                   AutoCompletion.TYPE_FILES)

    def do_copy(self, line):
        """Copies a file or directory (and its contents)."""
        line = line.split()
        if len(line) > 2:
            print(f"{Fore.RED}More than two arguments were found, they were ignored.")

        item_to_be_copied = os.path.join(self.current_directory, line[0])
        destination = os.path.join(self.current_directory, line[1])

        try:
            # verify that both locations exist
            if not os.path.exists(item_to_be_copied):
                raise FileNotFoundError(f"File '{item_to_be_copied}' not found.")
            if not os.path.exists(destination):
                raise FileNotFoundError(f"Destination '{destination}' not found.")

            # check if destination is an existing directory
            if os.path.isfile(destination):
                raise NotADirectoryError("Destination argument should be a directory, not a file.")

            # verify type before copying
            print(f"Copying...")
            if os.path.isdir(item_to_be_copied):
                shutil.copytree(item_to_be_copied, destination)
            else:
                shutil.copy(item_to_be_copied, destination)
            print(f"Copied: {item_to_be_copied} to {destination}")
        except PermissionError as e:
            print(f"{Fore.RED}Permission denied.")
        except FileExistsError as e:
            print(f"{Fore.RED}File already exists in this directory.")
        except (FileNotFoundError, NotADirectoryError) as e:
            print(f"{Fore.RED}{e}")
        except Exception as e:
            self.__on_error(e)

    def complete_copy(self, text, line, begidx, endidx):
        return AutoCompletion.path(self.current_directory, text, line, begidx, endidx)

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
        return AutoCompletion.path(self.current_directory, text, line, begidx, endidx)

    def do_zip(self, directory):
        """Zips a directory."""
        try:
            file_system.zip(directory)
            print(Fore.GREEN + f"Zipped: {directory}")
        except Exception as e:
            self.__on_error(e)

    def complete_zip(self, text, line, begidx, endidx):
        return AutoCompletion.path(self.current_directory, text, line, begidx, endidx)

    def do_unzip(self, zip_file):
        """Unzips a directory."""
        try:
            file_system.unzip(zip_file)
            print(Fore.GREEN + f"Unzipped: {zip_file}")
        except Exception as e:
            self.__on_error(e)

    def complete_unzip(self, text, line, begidx, endidx):
        return AutoCompletion.path(self.current_directory, text, line, begidx, endidx,
                                   AutoCompletion.TYPE_FILES)

    def do_fart(self, line):
        """Plays fart sound."""
        print(f"{cool_pepe}\nThppt! *Shits pants*")
        fart_sound_wav = os.path.join(self.script_wd, "res", "fart.wav")
        playsound(fart_sound_wav)

    def do_youtube(self, video_url):
        """Parses YouTube command(s)."""
        if not video_url:
            print(f"{Fore.RED}Video url missing.")
            return

        result = ListMenu.spawn(["Video + Audio", "Audio only"])
        if not result:
            return

        result = result.lower()
        audio_only = result == "audio only"
        success = youtube.downloader.download(video_url, audio_only)

        if success:
            print(f"\n{Fore.GREEN}Download completed!")
        else:
            print(f"\n{Fore.GREEN}Something went wrong.")

    def do_anime(self, line):
        """Anime."""
        result = ListMenu.spawn(["Watch Anime Offline", "Download Anime"])
        if not result:
            return

        verbose = "--verbose" in line

        # make preparations
        animes_dir = os.path.join(os.path.expanduser("~/Videos"), "anime")
        self.do_mkdir(animes_dir, silent=True)

        # actual
        result = result.lower()
        if result == "download anime":
            new_or_continue = ListMenu.spawn(["Continue anime", "New anime"],
                                             title="Do you wish to continue or start a new anime?")
            if not new_or_continue:
                return

            new_or_continue = new_or_continue.lower()
            if new_or_continue == "continue anime":
                # choose from downloaded animes
                downloaded_animes = file_system.get_directories_in_directory(animes_dir)
                anime_name = ListMenu.spawn(downloaded_animes, title="Which anime do you wish to continue?")
            elif new_or_continue == "new anime":
                # lookup anime
                anime_name = InputMenu.spawn("Anime Name: ")
                if not anime_name:
                    self.do_anime(line)
                    return
            else:
                return

            animes = anime.lookup.search_anime_by_name(anime_name)
            if not animes:
                print(f"{Fore.RED}No animes found with name: '{anime_name}'")
                return

            # choose anime
            chosen_anime = ListMenu.spawn(animes, "Choose an anime:")
            if not chosen_anime:
                return

            # choose episode
            episodes = anime.lookup.get_episodes_by_anime(chosen_anime)
            episode = ListMenu.spawn(episodes, "Choose an episode:", use_indexes=False)
            if not episode:
                return

            # download episode
            try:
                print(f"{Fore.GREEN}{anime_name} - Episode: {episode}")
                anime.downloader.download_episode(chosen_anime, int(episode), verbose=verbose)
                print()
                print(f"{Fore.GREEN}Successfully download episode {episode} from '{chosen_anime}'!")
            except Exception as e:
                self.__on_error(e)
        elif result == "watch anime offline":
            # choose anime
            animes = file_system.get_directories_in_directory(animes_dir)
            anime_name = ListMenu.spawn(animes, title="Choose an anime to watch:")
            if not anime_name:
                return

            # choose episode
            anime_dir = os.path.join(animes_dir, anime_name)
            episodes = file_system.get_files_in_directory(anime_dir)
            episodes = sorted([ep[0].removesuffix(".mp4") for ep in episodes if ep[0].endswith(".mp4")], key=int)

            episode = ListMenu.spawn(episodes, title="Choose an episode:")
            if not episode:
                return

            # play episode
            episode_file = os.path.join(anime_dir, f"{episode}.mp4")
            self.do_open(episode_file)

    def complete_anime(self, text, line, begidx, endidx):
        return ["--verbose"]

    def do_music(self, subcommand):
        """Opens music player. Currently only playlist support."""
        print("WIP!")
        print(music_pepe)

        if subcommand != "":
            if subcommand == "pause":
                music_player.pause()
            elif subcommand == "stop":
                music_player.stop()
            elif subcommand == "resume" or subcommand == "play":
                music_player.resume()
            elif subcommand == "playing":
                print(f"{Fore.GREEN}Currently playing: {Fore.WHITE}{music_player.now_playing.name}")
            elif subcommand == "visualizer":
                print("Experimental, not ready for use... ")

                visualizer = MusicVisualizer()
                visualizer.start_visualization()
                visualizer.close_stream()
            else:
                self.default(subcommand)
            return

        # look for available playlists
        playlists = file_system.get_directories_in_directory(os.path.join(os.path.expanduser("~/Music"), "Playlists"))
        if not playlists:
            print(f"{Fore.RED}No playlists found.")
            return

        # let the user pick a playlist
        playlist_name = ListMenu.spawn(playlists, title="Choose a playlist:")
        if not playlist_name:
            return

        # stop current music before continuing
        if music_player.now_playing:
            music_player.stop()

        # load & play the selected playlist
        playlist = MusicPlayer.load_playlist_by_name(playlist_name)
        print(
            f"{Fore.GREEN}Picked playlist {Fore.WHITE}{playlist.name}{Fore.GREEN} with {Fore.WHITE}{len(playlist.songs)}{Fore.GREEN} song(s)."
        )
        music_player.play_playlist(playlist)

    def complete_music(self, text, line, begidx, endidx):
        subcommands = ["pause", "stop", "resume", "play", "playing", "visualizer"]
        return AutoCompletion.matches_of(subcommands, text, line, begidx, endidx)

    def do_config(self, line):
        """Opens config editor."""
        # select section
        sections = [item[0] for item in self.config.config.items()]  # because config.sections() doesn't include DEFAULT
        section = ListMenu.spawn(sections, "Section")
        if not section:
            return

        # fix data because configparser is stupid
        if section == "DEFAULT":
            # because technically DEFAULT section doesn't exist (this is so dumb...)
            # to avoid: 'dict_keys' object is not subscriptable
            options = [key for key in self.config.config.defaults().keys()]
        else:
            options = self.config.config.options(section)

            # remove default options because they're for some reason there
            default_options = self.config.config.defaults().keys()
            options = [opt for opt in options if opt not in default_options]

        # select option
        option = ListMenu.spawn(options, "Option")
        if not option:
            return

        # change option value
        old_value = self.config.config.get(section, option)
        new_value = InputMenu.spawn(f"{option}=", title=f"Change option '{option}'? (Current: {old_value})").strip()

        if new_value == "":
            # nothing happens
            return

        # confirm change
        confirmation = ListMenu.spawn(
            ["Confirm", "Cancel"],
            title=f"{option}: {old_value} -> {new_value}?",
            quittable=False
        ).lower()

        if confirmation == "cancel":
            # again nothing happens
            return

        # save changes
        self.config.config[section][option] = new_value
        self.config.save_config()
        self.config.reload()

    def do_time(self, line):
        """Shows current date (along with day of week) and time."""
        line = line.strip()
        if not line:
            line = "now"

        parts = line.strip().split()
        subcommand = parts[0]

        try:
            if subcommand == "now":
                current_datetime = datetime.now()
                formatted_date = current_datetime.strftime("%Y-%m-%d")
                formatted_time = current_datetime.strftime("%H:%M:%S")
                formatted_day = current_datetime.strftime("%A")
                print(
                    f"Today's date is {Fore.GREEN}{formatted_date}{Fore.RESET}, it's a {Fore.GREEN}{formatted_day}{Fore.RESET} and it's currently {Fore.GREEN}{formatted_time}{Fore.RESET}."
                )
            elif subcommand == "wunix":
                if len(parts) < 2:
                    self.default(line)
                    return

                unix_time = int(parts[1])
                dt = datetime.fromtimestamp(unix_time)
                formatted_date = dt.strftime("%Y-%m-%d")
                formatted_time = dt.strftime("%H:%M:%S")
                formatted_day = dt.strftime("%A")

                print(
                    f"Unix timestamp {Fore.GREEN}{unix_time}{Fore.RESET} corresponds to {Fore.GREEN}{formatted_date}{Fore.RESET}, {Fore.GREEN}{formatted_day}{Fore.RESET} at {Fore.GREEN}{formatted_time}{Fore.RESET}."
                )
            else:
                self.default(line)
        except Exception as e:
            self.__on_error(e)

    def complete_time(self, text, line, begidx, endidx):
        commands = ["now", "wunix"]
        return AutoCompletion.matches_of(commands, text, line, begidx, endidx)

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

    def do_com(self, line):
        """Allows interaction with COM port(s)."""
        if line:
            subcommand = line
        else:
            subcommand = ListMenu.spawn(["Scan"])

        if not subcommand:
            return

        subcommand = subcommand.lower()
        if subcommand == "scan":
            connections = com.connections
            print(f"{Fore.GREEN}Connections:")
            if connections:
                print(*connections)
            else:
                print("No connections to COM port(s).")
        else:
            self.default(subcommand)

    def do_horserace(self, line):
        line = line.strip()
        if line == "":
            horses_count = 5
        elif not is_integer(line):
            self.default(line)
            return
        else:
            horses_count = int(line)

        race = HorseRace(horses_count)
        race.start()
        print(f"\n{Fore.GREEN}{race.winner} came out on top as the best of {horses_count} horses!")

    def do_search(self, query):
        """Searches a specified place for something to match the given query."""
        query = query.strip()
        search_type = ListMenu.spawn(["Web", "Locally"], "Where do you want to search?")
        if not search_type:
            return

        search_type = search_type.lower()
        if search_type == "web":
            print(f"{Fore.LIGHTBLACK_EX}Searching the web for: '{query}'...")
            results = web_searcher.search(query)
        elif search_type == "locally":
            home_dir = os.path.expanduser("~/Desktop")
            root = InputMenu.spawn("Path: ",
                                   title=f"Choose a starting directory to perform the search in (Default={home_dir})")
            if not root:
                root = home_dir

            print(f"{Fore.LIGHTBLACK_EX}Searching locally for: '{query}'...")
            local_searcher.search_threshold = self.config.config.getint(section="DEFAULT", option="search_threshold")
            results = local_searcher.search(directories=[root], fn_query=query)
        else:
            self.default(query)
            return

        result = ListMenu.spawn([r.title for r in results], f"Search results ({len(results)})")
        selected_result = next((r for r in results if r.title == result), None)
        if not selected_result:
            return

        if search_type == "web":
            webbrowser.open(selected_result.location, new=0, autoraise=True)
        else:
            self.do_open(selected_result.location)

    def do_clear(self, line):
        """Clears screen."""
        os.system(self.clear_command)
        if self.config.config.getboolean(section="DEFAULT", option="display_intro"):
            print(self.intro)

    def do_q(self, line):
        """Exit CLI."""
        return True

    def do_reload(self, line):
        """Reloads/Restarts the CLI."""
        if line == "config":
            print(f"{Fore.CYAN}[!] Reloading config...")
            self.config.reload()
            print(f"{Fore.CYAN}Reloaded config!")
            return

        print(f"{Fore.LIGHTBLACK_EX}Running postloop...")
        history_manager.record_line(f"reload {line}")
        self.postloop()

        print(f"{Fore.WHITE}Reloading...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def do__history(self, line):
        """Allows you to inspect the command history."""
        line = line.strip()
        if line.lower() == "reset":
            confirmation = ListMenu.spawn(["Yes", "No"])
            if confirmation and confirmation.lower() == "yes":
                history_manager.history = []
                print(f"{Fore.GREEN}Reset command history.")
            return
        elif line:
            self.default(line)
            return

        limit = 25
        valid_commands = [name.removeprefix("do_") for name in self.get_names() if name.startswith("do_")]
        for record in history_manager.history[::-1][:min(limit, len(history_manager.history))]:
            timestamp = f"{Fore.LIGHTBLACK_EX}{int(record.timestamp.timestamp())}{Fore.RESET}"
            command_color = Fore.GREEN if record.command in valid_commands else Fore.RED
            command = f"{command_color}{record.command}{Fore.RESET}"
            subcommands = f"{Fore.LIGHTGREEN_EX}{' '.join(record.subcommands).strip()}{Fore.RESET}"
            print(timestamp, command, subcommands)

        if len(history_manager.history) > limit:
            print(f"\n{Fore.WHITE}And {len(history_manager.history) - limit} more...")

    def do__cache(self, line):
        """Allows you to inspect the cache of certain commands."""
        if line.strip() == "--force-postloop-now":
            print(f"{Fore.LIGHTGREEN_EX}Forcing postloop routine...")
            self.postloop()
            print(f"{Fore.GREEN}Complete!")
            return

        commands = [name.removeprefix("do_") for name in self.get_names() if name.startswith("do_")]

        # get valid command files
        command_files = []
        for file in os.listdir(cache_directory):
            filename = os.path.splitext(file)[0]
            if filename in commands:
                command_files.append(file)

        # pick a command file
        if line:
            command = line.strip()
            if command not in commands:
                self.default(line)
                return

            command_file = None
            for file in command_files:
                if os.path.splitext(file)[0] == command:
                    command_file = file
                    break
        else:
            command_file = ListMenu.spawn(command_files)

        # no cache available or no option was selected in the menu
        if not command_file:
            return

        # display chosen command's cache
        content = file_system.get_file_content_binary(os.path.join(cache_directory, command_file))
        stringified_content = json.dumps(content, indent=2, sort_keys=True, cls=SearchResultEncoder)
        TextPane.display(stringified_content, title=command_file.upper(), show_lines_in_title=True)

    def complete__cache(self, text, line, begidx, endidx):
        commands = [name.removeprefix("do_") for name in self.get_names() if name.startswith("do_")]
        commands.append("--force-postloop-now")
        return AutoCompletion.matches_of(commands, text, line, begidx, endidx)
