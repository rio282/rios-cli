import configparser
import os
from typing import Optional


class Config:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        if not os.path.exists(config_dir):
            # make the config dir if it doesn't exist
            os.mkdir(config_dir)

        self.main_config = os.path.join(self.config_dir, "main.config")
        self.config = configparser.ConfigParser()
        self.reload()

    def reload(self):
        self.config.read(self.main_config)

    def save_config(self, config_file: Optional[str] = "") -> None:
        if config_file == "":
            config_file = self.main_config

        with open(file=config_file, mode="w") as configfile:
            self.config.write(configfile)

    def create_default_config(self) -> None:
        # default settings
        self.config["DEFAULT"] = {
            "search_threshold": "50",
            "display_intro": "yes",
        }

        # save
        self.save_config()
        self.reload()
