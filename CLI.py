import cmd
import os
import sys
import shutil
import webbrowser

from psutil._common import bytes2human

from colorama import init, Fore
from pprint import pprint

from etc.utils import truncate_filename, AutoCompletion, is_integer
from etc.pepes import *
from services import youtube, anime, file_system, network, com, processes, statistics, web_searcher, local_searcher
from services.price_charting import Tracker
from services.cursive import InteractiveMenu, SliderMenu, TextPane
from services.cursive.editors import InputMenu
from typing import Final, List, Tuple
from playsound import playsound
from datetime import date, datetime

from services.music import MusicPlayer, music_player
from services.osys import AudioService
from services.search.web import WebSearchResult
from services.internal.config import Config

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

        # load tracker
        self.tracker = Tracker(self.config.config.get(section="PRICE CHARTING", option="listing_file"),
                               self.config.config.getint(section="PRICE CHARTING", option="refresh_time_minutes"))

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
        return stop

    def preloop(self):
        file_system.load_cache()
        web_searcher.load_cache()

    def postloop(self):
        if self.tracker.running:
            self.tracker.stop()

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
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx,
                                                AutoCompletion.FILES)

    def do_copy(self, filename):
        """Copies a file or directory."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            if not os.path.exists(file_path):
                print(f"File '{filename}' not found.")
                return

            destination = os.path.join(self.current_directory, filename)

            if os.path.isdir(file_path):
                shutil.copytree(file_path, destination)
            else:
                shutil.copy(file_path, destination)

            print(f"Copied: {file_path} to {destination}")
        except PermissionError as e:
            print(f"{Fore.RED}Permission denied.")
        except FileExistsError as e:
            print(f"{Fore.RED}File already exists in this directory.")
        except Exception as e:
            self.__on_error(e)

    def complete_copy(self, text, line, begidx, endidx):
        return AutoCompletion.autocomplete_path(self.current_directory, text, line, begidx, endidx)

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
        """Parses YouTube command(s). (PyTube is currently broken)."""
        if not video_url:
            print(f"{Fore.RED}Video url missing.")
            return

        result = InteractiveMenu.spawn(["Video + Audio", "Audio only", "Exit"]).lower()
        if result == "exit":
            return

        audio_only = result == "audio only"
        success = youtube.downloader.download(video_url, audio_only)

        if success:
            print(f"\n{Fore.GREEN}Download completed!")
        else:
            print(f"\n{Fore.GREEN}Something went wrong.")

    def do_anime(self, line):
        """Anime."""
        result = InteractiveMenu.spawn(["Watch Anime Offline", "Download Anime", "Exit"]).lower()
        if result == "exit":
            return

        verbose = "--verbose" in line

        # make preparations
        animes_dir = os.path.join(os.path.expanduser("~/Videos"), "anime")
        self.do_mkdir(animes_dir, silent=True)

        # actual
        if result == "download anime":
            new_or_continue = InteractiveMenu.spawn(["Continue anime", "New anime", "Exit"],
                                                    title="Do you wish to continue or start a new anime?").lower()
            if new_or_continue == "continue anime":
                # choose from downloaded animes
                downloaded_animes = file_system.get_directories_in_directory(animes_dir)
                anime_name = InteractiveMenu.spawn(downloaded_animes, title="Which anime do you wish to continue?")
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
            chosen_anime = InteractiveMenu.spawn(animes, "Choose an anime:")

            # choose episode
            episodes = anime.lookup.get_episodes_by_anime(chosen_anime)
            episode = InteractiveMenu.spawn(episodes, "Choose an episode:", use_indexes=False)

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
            animes.append("Exit")
            anime_name = InteractiveMenu.spawn(animes, title="Choose an anime to watch:")
            if anime_name.lower() == "exit":
                return

            # choose episode
            anime_dir = os.path.join(animes_dir, anime_name)
            episodes = file_system.get_files_in_directory(anime_dir)
            episodes = sorted([ep[0].removesuffix(".mp4") for ep in episodes if ep[0].endswith(".mp4")], key=int)

            episodes.append("Exit")
            episode = InteractiveMenu.spawn(episodes, title="Choose an episode:")
            if episode.lower() == "exit":
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

        if subcommand == "":
            pass
        else:
            if subcommand == "pause":
                music_player.pause()
            elif subcommand == "stop":
                music_player.stop()
            elif subcommand == "resume" or subcommand == "play":
                music_player.resume()
            else:
                self.default(subcommand)
            return

        playlists = file_system.get_directories_in_directory(os.path.join(os.path.expanduser("~/Music"), "Playlists"))
        playlist_name = InteractiveMenu.spawn(playlists, title="Choose a playlist:")

        # stop current stuff before continuing
        if music_player.now_playing:
            music_player.stop()

        playlist = MusicPlayer.load_playlist_by_name(playlist_name)
        music_player.play_playlist(playlist)

    def do_config(self, line):
        """Opens config editor."""
        # select section
        sections = [item[0] for item in self.config.config.items()]  # because config.sections() doesn't include DEFAULT
        section = InteractiveMenu.spawn(sections, "Section")

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
        option = InteractiveMenu.spawn(options, "Option")

        # change option value
        old_value = self.config.config.get(section, option)
        new_value = InputMenu.spawn(f"{option}=", title=f"Change option '{option}'? (Current: {old_value})").strip()

        if new_value == "":
            # nothing happens
            return

        # confirm change
        confirmation = InteractiveMenu.spawn(
            ["Confirm", "Cancel"],
            title=f"{option}: {old_value} -> {new_value}?"
        ).lower()

        if confirmation == "cancel":
            # again nothing happens
            return

        # save changes
        self.config.config[section][option] = new_value
        self.config.save_config()
        self.config.reload()

    def do_ptrackers(self, subcommand):
        """Price trackers for different sites."""
        if not subcommand:
            print(
                f"{Fore.GREEN}Tracked (Items: {len(self.tracker.products)}, Last tracked: {self.tracker.last_tracked}):"
            )
            print(*self.tracker.products)
        elif subcommand == "start":
            if self.tracker.running:
                print(f"{Fore.RED}Price tracker already running...")
                return
            self.tracker.start()
            print(f"{Fore.GREEN}Price tracker started.")
        elif subcommand == "stop":
            if not self.tracker.running:
                print(f"{Fore.RED}Price tracker is not running.")
                return
            self.tracker.stop()
            print(f"{Fore.GREEN}Price tracker stopped.")
        else:
            self.default(subcommand)

    def complete_ptrackers(self, text, line, begidx, endidx):
        subcommands = ["start", "stop"]
        return AutoCompletion.autocomplete_closer_match_of(subcommands, text, line, begidx, endidx)

    def do_now(self, line):
        """Shows current date (along with day of week) and time."""
        current_datetime = datetime.now()
        formatted_date = current_datetime.strftime("%Y-%m-%d")
        formatted_time = current_datetime.strftime("%H:%M:%S")
        formatted_day = current_datetime.strftime("%A")
        print(
            f"Today's date is {Fore.GREEN}{formatted_date}{Fore.RESET}, it's a {Fore.GREEN}{formatted_day}{Fore.RESET} and it's currently {Fore.GREEN}{formatted_time}{Fore.RESET}."
        )

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

            if subcommand == "key":
                ssid_password = network.get_ssid_password()
                print(Fore.GREEN + ssid_password)
            else:
                print(Fore.RED + "Unknown subcommand specified.")
        except Exception as e:
            self.__on_error(e)

    def do_com(self, line):
        """Allows interaction with COM port(s)."""
        if line:
            subcommand = line
        else:
            subcommand = InteractiveMenu.spawn(["Scan", "Exit"]).lower()

        if subcommand == "exit":
            return
        elif subcommand == "scan":
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
            local_searcher.search_threshold = self.config.config.getint(section="DEFAULT", option="search_threshold")
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
        self.postloop()

        print(f"{Fore.WHITE}Reloading...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
