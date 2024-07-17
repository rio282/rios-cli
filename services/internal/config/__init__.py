import configparser
import os


class Config:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        if not os.path.exists(config_dir):
            # make the config dir if it doesn't exist
            os.mkdir(config_dir)

        self.config_file = os.path.join(self.config_dir, "app.config")
        self.config = configparser.ConfigParser()
        self.reload()

    def reload(self) -> None:
        self.config.read(self.config_file)

    def save_config(self) -> None:
        with open(file=self.config_file, mode="w") as configfile:
            self.config.write(configfile)

    def create_default_config(self) -> None:
        self.__overwrite_default_section()
        self.__overwrite_cardmarket_section()

        # save
        self.save_config()
        self.reload()

    def __overwrite_default_section(self) -> None:
        self.config["DEFAULT"] = {
            "search_threshold": "50",
            "display_intro": "yes",
        }

    def __overwrite_cardmarket_section(self) -> None:
        cardmarket_listing_file = "./cardmarket.csv"
        cardmarket_listing_file_path = cardmarket_listing_file.replace("./", f"{self.config_dir}/")
        if not os.path.exists(cardmarket_listing_file_path):
            open(file=cardmarket_listing_file_path, mode="x")

        self.config["CARDMARKET"] = {
            "refresh_time_minutes": f"{12 * 60}",
            "listing_file": cardmarket_listing_file_path
        }
