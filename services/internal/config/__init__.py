import configparser
import os


class Config:
    def __init__(self):
        self.config_file_location = os.path.join(os.getcwd(), ".config", "cli.config")
        self.config = configparser.ConfigParser()

    def create_default_config(self) -> None:
        # default settings
        self.config["DEFAULT"] = {
            "search_threshold": "50",
            "test": "yes",
            "test1": "no"
        }

        # save
        self.save_config()

    def save_config(self) -> None:
        with open(file=self.config_file_location, mode="w") as configfile:
            self.config.write(configfile)
