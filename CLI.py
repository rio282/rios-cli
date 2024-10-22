import cmd
import json
import os
import shutil
import sys
import webbrowser
from datetime import date, datetime
from typing import List

import psutil
from colorama import init, Fore
from tabulate import tabulate

from etc.pepes import *
from etc.utils import truncate_filename, AutoCompletion, is_integer, playsound_deferred, FuzzyMatcher
from games.horse_racing import HorseRace
from services import youtube, anime, file_system, com, processes, web_searcher, local_searcher, \
    history_manager, cache_directory
from services.cursive.display import TextPane, MusicVisualizer
from services.cursive.input import ListMenu, SliderMenu, InputMenu
from services.internal import SerializedEncoder, CommandArgsParser
from services.internal.config import Config
from services.music import MusicPlayer, music_player
from services.osys import AudioService
from services.osys.fs import File
from services.osys.info import display_sysinfo

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
    nohelp: str = f"*** %s? What's that? -- I wonder who forgot to write documentation about this command... {Fore.WHITE}*ahem*{Fore.RESET}"
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

    def list_files(self, files: List[File]):
        print()
        print(f"{Fore.GREEN}Files ({len(files)}):")

        if not files:
            return

        table_data = []
        max_length = 48

        for file in files:
            base_name, file_ext = os.path.splitext(file.name)

            truncated_name = truncate_filename(base_name, file_ext, max_length)
            filename_display = f"{Fore.LIGHTBLACK_EX}{truncated_name}{Fore.RESET}" \
                if file.name.startswith(".") else truncated_name
            file_size_mb_rounded = float(f"{file.size_mb:.2f}")
            file_size_display = f"{Fore.CYAN}{file_size_mb_rounded} MB" if file_size_mb_rounded > 0 else f"{Fore.CYAN}~{file_size_mb_rounded} MB"
            file_type = file_system.get_file_type(file_ext)
            last_updated = datetime.fromtimestamp(file.last_updated).strftime("%Y-%m-%d %H:%M:%S").split()
            last_updated = f"{last_updated[0]} {Fore.LIGHTBLACK_EX}{last_updated[1]}{Fore.RESET}"

            table_data.append([filename_display, file_size_display, file_type, last_updated, file.file_hash])

        print(tabulate(
            table_data,
            headers=[f"{Fore.WHITE}Filename", "Size", "Type", "Updated", f"Hash{Fore.RESET}"],
            colalign=("left", "right", "left", "left", "right")
        ))

    def list_directories(self, directories: List[str]):
        print()
        print(f"{Fore.GREEN}Directories ({len(directories)}):")
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
        anime.lookup.load()
        history_manager.load()

    def postloop(self):
        file_system.save()
        local_searcher.save()
        web_searcher.save()
        anime.lookup.save()
        history_manager.save()

    def emptyline(self):
        pass

    def do_hello(self, name):
        """Replies with 'Hi!' or 'Hello <name>!'"""
        if not name:
            print("Hi!")
        else:
            print(f"Hello {name}!")

    def do_ping(self, _):
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
        del line, begidx, endidx
        return AutoCompletion.path(self.current_directory, text, AutoCompletion.TYPE_DIRECTORIES)

    def do_ls(self, line):
        """Lists the files and directories in a directory. Options: [--cache, --chashes, --file(s), --dir(s), --match <QUERY>]"""
        try:
            directory = file_system.clean_directory(line, filter_args=True)
            is_zip_file = os.path.isfile(directory) and os.path.splitext(directory)[1] == ".zip"

            # parse args
            parser = CommandArgsParser(line)

            print_dirs = parser.is_arg_present("dirs") or parser.is_arg_present("dir")
            print_files = parser.is_arg_present("files") or parser.is_arg_present("file")
            if not print_dirs and not print_files:
                print_dirs = True
                print_files = True

            use_cache = parser.is_arg_present("cache")
            calculate_hashes = parser.is_arg_present("chashes")

            perform_matching = parser.is_arg_present("match")
            match_query = parser.get_value_of_arg("match")
            if perform_matching:
                FuzzyMatcher.required_matching_score = self.config.config.getint(section="DEFAULT",
                                                                                 option="search_threshold")

            # zip files
            if is_zip_file:
                zip_content = file_system.get_zip_content(directory)
                if print_dirs:
                    self.list_directories(zip_content.get("directories"))
                if print_files:
                    self.list_files(zip_content.get("files"))
                return

            # normal directories
            if print_dirs:
                directories = file_system.get_directories_in_directory(directory, use_cache)
                if perform_matching and match_query:
                    directories = AutoCompletion.matches_of(directories, match_query,
                                                            completion_mode=AutoCompletion.MODE_MATCH_ANY)
                self.list_directories(directories)
            if print_files:
                files = file_system.get_files_in_directory(directory, use_cache, calculate_hashes)
                if perform_matching and match_query:
                    files = AutoCompletion.matches_of(files, match_query,
                                                      completion_mode=AutoCompletion.MODE_MATCH_ANY)
                self.list_files(files)
        except Exception as e:
            self.__on_error(e)

    def complete_ls(self, text, line, begidx, endidx):
        del line, begidx, endidx
        matches = AutoCompletion.path(
            self.current_directory,
            text,
            AutoCompletion.TYPE_DIRECTORIES_AND_ZIP
        )
        arg_matches = AutoCompletion.matches_of(
            ["--cache", "--chashes", "--file", "--files", "--dir", "--dirs", "--match"],
            text
        )

        matches.extend(arg_matches)
        return matches

    def do_open(self, filename):
        """Opens a file in the specified path."""
        file_path = os.path.join(self.current_directory, filename)
        try:
            os.startfile(file_path)
        except FileNotFoundError:
            print(f"{Fore.RED}File '{filename}' not found.")
        except Exception as e:
            self.__on_error(e)

    def complete_open(self, text, line, begidx, endidx):
        del line, begidx, endidx
        return AutoCompletion.path(self.current_directory, text)

    def do__owd(self, line):
        """Opens the original working directory. (Add a '?' to display the path)"""
        if line.strip() == "?":
            print(self.script_wd)
        else:
            self.do_open(self.script_wd)

    def do_mkfile(self, filename):
        """Create a new file in the current directory."""
        filename = filename.strip()
        file_path = os.path.join(self.current_directory, filename)
        try:
            if os.path.exists(file_path):
                print(f"Directory '{file_path}' already exists in directory '{file_path.removesuffix(filename)}'")
            else:
                with open(file_path, "w"):
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
        del line, begidx, endidx
        return AutoCompletion.path(self.current_directory, text, AutoCompletion.TYPE_FILES)

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
            print(f"{Fore.RED}Not found. {e}")
        except Exception as e:
            self.__on_error(e)

    def complete_copy(self, text, line, begidx, endidx):
        del line, begidx, endidx
        return AutoCompletion.path(self.current_directory, text)

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
        del line, begidx, endidx
        return AutoCompletion.path(self.current_directory, text)

    def do_zip(self, line):
        """Zips a directory."""
        directory = file_system.clean_directory(line, filter_args=True)
        parser = CommandArgsParser(line)

        try:
            password = parser.get_value_of_arg("password")
            success = file_system.zip(directory, with_password=password)
            if success:
                print(f"{Fore.GREEN}Zipped: {directory}")
            else:
                print(f"{Fore.RED}Something unexpected went wrong...")
        except Exception as e:
            self.__on_error(e)

    def complete_zip(self, text, line, begidx, endidx):
        del line, begidx, endidx
        return AutoCompletion.path(self.current_directory, text)

    def do_unzip(self, line):
        """Unzips a directory."""
        zip_file = file_system.clean_directory(line, filter_args=True)
        parser = CommandArgsParser(line)

        try:
            password = parser.get_value_of_arg("password")
            success = file_system.unzip(zip_file, with_password=password)
            if success:
                print(f"{Fore.GREEN}Unzipped: {zip_file}")
            else:
                print(f"{Fore.RED}Something unexpected went wrong...")
        except RuntimeError:
            print(f"{Fore.RED}This operation threw a RuntimeError...")
            print(f"\t{Fore.RED} -> File '{zip_file}' is most-likely encrypted with a password.")
        except Exception as e:
            self.__on_error(e)

    def complete_unzip(self, text, line, begidx, endidx):
        del line, begidx, endidx
        return AutoCompletion.path(self.current_directory, text, AutoCompletion.TYPE_FILES)

    def do_fart(self, _):
        """Plays fart sound."""
        fart_sound_wav = os.path.join(self.script_wd, "res", "fart.wav")
        playsound_deferred(fart_sound_wav)
        print(f"{cool_pepe}\nThppt! *Shits pants*")

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
        force_refresh = "--refresh" in line

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
                anime_name = anime_name.strip()
            else:
                return

            animes = anime.lookup.search_anime_by_name(anime_name, force_refresh=force_refresh)
            if not animes:
                print(f"{Fore.RED}No animes found with name: '{anime_name}'")
                return

            dt = datetime.fromtimestamp(anime.lookup.animes_cache[anime_name][0])
            formatted_dt = dt.strftime("%Y-%m-%d @ %H:%M:%S")
            print(f"{Fore.LIGHTGREEN_EX}Search results for query '{anime_name}' were last updated on {formatted_dt}.")
            print(f"{Fore.LIGHTGREEN_EX}Use the '--refresh' flag to force-refresh the search results.")
            print()

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
            episodes = sorted([ep.name.removesuffix(".mp4") for ep in episodes if ep.name.endswith(".mp4")], key=int)

            episode = ListMenu.spawn(episodes, title="Choose an episode:")
            if not episode:
                return

            # play episode
            episode_file = os.path.join(anime_dir, f"{episode}.mp4")
            self.do_open(episode_file)

    def complete_anime(self, text, line, begidx, endidx):
        del line, begidx, endidx
        subcommands = ["--verbose", "--refresh"]
        return AutoCompletion.matches_of(subcommands, text)

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
        del line, begidx, endidx
        subcommands = ["pause", "stop", "resume", "play", "playing", "visualizer"]
        return AutoCompletion.matches_of(subcommands, text)

    def do_config(self, _):
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
        parser = CommandArgsParser(line)
        subcommand = parser.args_raw[0] if parser.args_raw else "now"

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
                unix_time_str = parser.get_value_of_arg("wunix")
                if not unix_time_str:
                    self.default(line)
                    return

                unix_time = int(unix_time_str)
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
        del line, begidx, endidx
        commands = ["now", "wunix"]
        return AutoCompletion.matches_of(commands, text)

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

    def do_sysinfo(self, _):
        """Device statistics."""
        display_sysinfo()

    def do_netstat(self, _):
        """Some network statistics."""
        connections = psutil.net_connections(kind="inet")
        rows = []

        for conn in connections:
            if conn.status == "ESTABLISHED":
                laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
                raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
                pid = conn.pid

                try:
                    process = psutil.Process(pid)
                    pname = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pname = "-"

                rows.append((
                    f"{Fore.GREEN}{pid}{Fore.RESET}",
                    f"{laddr.split(':').pop().ljust(5)} -> {raddr.split(':').pop().rjust(5)}:{Fore.CYAN}{raddr.split(':')[0]}{Fore.RESET}",
                    f"{pname}"
                ))

        rows = sorted(rows, key=lambda x: x[2])  # NOTE: WATCH OUT WITH THIS LINE WHEN CHANGING THE CODE OF THIS METHOD
        headers = [f"{Fore.WHITE}PID", "Connected To", f"Name{Fore.RESET}"]
        print(f"\n{Fore.GREEN}*** Open connection(s):\n")
        print(tabulate(rows, headers=headers))

    def do_com(self, line):
        """Allows interaction with COM port(s)."""
        subcommand = line if line else ListMenu.spawn(["Scan"])
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
        """Horse races! Parameter can set the amount of horses (default=5)."""
        parser = CommandArgsParser(line)
        no_sound = parser.is_arg_present("silent")
        horses_count_str = parser.get_value_of_arg("horses")

        if not horses_count_str:
            horses_count = 5  # default number of horses
        elif not is_integer(horses_count_str):
            self.default(line)
            return
        else:
            horses_count = int(horses_count_str)

        try:
            race = HorseRace(horses_count)

            if not no_sound:
                horse_sound_wav = os.path.join(self.script_wd, "res", "horse.wav")
                playsound_deferred(horse_sound_wav)

            race.start()
            print(
                f"\n{Fore.GREEN}{race.winner} (no. {race.winning_number}) came out on top as the best of {horses_count} horses!"
            )
        except AttributeError as e:
            print(f"{Fore.RED}{e}")
        except Exception as yeah_we_messed_up:
            self.__on_error(yeah_we_messed_up)

    def complete_horserace(self, text, line, begidx, endidx):
        del line, begidx, endidx
        return AutoCompletion.matches_of(["--silent", "horses <amount>"], text)

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

    def do_clear(self, _):
        """Clears screen."""
        os.system(self.clear_command)
        if self.config.config.getboolean(section="DEFAULT", option="display_intro"):
            print(self.intro)

    def do_q(self, _):
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
        history_manager.record_line(f"reload {line}")  # doesn't get saved otherwise
        self.postloop()

        print(f"{Fore.WHITE}Reloading...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def do__history(self, line):
        """Allows you to inspect the command history."""
        line = line.strip()
        if line:
            subcommand = line.strip().lower()
            if subcommand == "reset":
                confirmation = ListMenu.spawn(["Yes", "No"])
                if confirmation and confirmation.lower() == "yes":
                    history_manager.history = []
                    print(f"{Fore.GREEN}Reset command history.")
            elif subcommand == "checkout":
                TextPane.display(history_manager.history, title="Checkout Full History", show_lines_in_title=True)
            elif subcommand in ("on", "off"):
                toggled_on = subcommand == "on"
                if not toggled_on:  # won't register this line otherwise
                    history_manager.record_line(line)

                history_manager.is_tracking = toggled_on
                print(f"{Fore.GREEN}History manager is now {'' if toggled_on else 'NOT '}TRACKING")
            elif line:
                self.default(line)
            return

        max_log_length = 25
        valid_commands = [name.removeprefix("do_") for name in self.get_names() if name.startswith("do_")]
        for record in history_manager.history[::-1][:min(max_log_length, len(history_manager.history))]:
            timestamp = f"{Fore.LIGHTBLACK_EX}{int(record.timestamp.timestamp())}{Fore.RESET}"
            command_color = Fore.GREEN if record.command in valid_commands else Fore.RED
            command = f"{command_color}{record.command}{Fore.RESET}"
            subcommands = f"{Fore.LIGHTGREEN_EX}{' '.join(record.subcommands).strip()}{Fore.RESET}"
            print(timestamp, command, subcommands)

        if len(history_manager.history) > max_log_length:
            print(f"\n{Fore.WHITE}And {len(history_manager.history) - max_log_length} more...")

    def complete__history(self, text, line, begidx, endidx):
        del line, begidx, endidx
        commands = ["reset", "checkout", "on", "off"]
        return AutoCompletion.matches_of(commands, text)

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
        stringified_content = json.dumps(content, indent=2, sort_keys=True, cls=SerializedEncoder)
        TextPane.display(stringified_content, title=command_file.upper(), show_lines_in_title=True)

    def complete__cache(self, text, line, begidx, endidx):
        del line, begidx, endidx
        commands = [name.removeprefix("do_") for name in self.get_names() if name.startswith("do_")]
        commands.append("--force-postloop-now")
        return AutoCompletion.matches_of(commands, text)
