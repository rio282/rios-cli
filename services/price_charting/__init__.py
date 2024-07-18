import csv
import datetime
import os
import re
from threading import Thread
from time import sleep
from typing import List, Optional, Dict, Any

import requests
from bs4 import BeautifulSoup

from etc.utils import collapse_spaces


class Product:
    def __init__(self, url: str, name: Optional[str] = None, prices: Optional[Dict[str, float]] = None):
        self.url = url
        self.name = name
        self.prices = prices

    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> "Product":
        url = _dict.get("url")
        name = _dict.get("name")
        prices = _dict.get("prices")

        return Product(url, name, prices)

    @staticmethod
    def to_dict(_product: "Product") -> Dict[str, Any]:
        return {
            "url": _product.url,
            "name": _product.name,
            "prices": _product.prices
        }

    def __repr__(self):
        if self.prices:
            return f"{self.name}: {self.prices}"
        return self.name if self.name else f"UNKNOWN <{self.url}>"


class Tracker:
    def __init__(self, csv_listing_file: str, refresh_time_minutes: int):
        self.listing_file = csv_listing_file
        self.refresh_time_minutes = refresh_time_minutes
        self.products = []

        self.__last_tracked = None
        self.__running = False

    def load_products_from_listing_file(self) -> List[Product]:
        if not os.path.exists(self.listing_file):
            raise FileNotFoundError

        with open(self.listing_file) as listing_file:
            reader = csv.reader(listing_file)
            headers = next(reader, None)
            products = [Product.from_dict({header: item for (header, item) in zip(headers, row)}) for row in reader]

        return products

    def save_products_to_listing_file(self) -> bool:
        if not os.path.exists(self.listing_file):
            raise FileNotFoundError

        # lol
        if not self.products:
            return False

        # get headers
        with open(self.listing_file, mode="r", newline="") as listing_file:
            reader = csv.reader(listing_file)
            headers = next(reader, None)

        # save
        with open(file=self.listing_file, mode="w", newline="") as listing_file:
            writer = csv.writer(listing_file)
            writer.writerow(headers)
            for product in self.products:
                product_data = Product.to_dict(product)
                row = [product_data.get(header, "") for header in headers]
                writer.writerow(row)

        return True

    def start(self) -> None:
        def run():
            while self.__running:
                self.products = self.load_products_from_listing_file()

                self.products = Scraper.scrape_products(self.products)
                self.__last_tracked = datetime.datetime.now()

                self.save_products_to_listing_file()
                sleep(self.refresh_time_minutes * 60)

        self.__running = True
        thread = Thread(target=run, daemon=False)
        thread.start()

    def stop(self) -> None:
        self.__running = False

    @property
    def running(self) -> bool:
        return self.__running

    @property
    def last_tracked(self) -> datetime:
        return self.__last_tracked


class Scraper:
    @staticmethod
    def __extract_forex_rates(script_str: str):
        pattern = re.compile(r"VGPC\.forex_rates\s*=\s*(\{.*?\});", re.DOTALL)
        match = pattern.search(script_str)

        if match:
            forex_rates_str = match.group(1)
            forex_rates = eval(forex_rates_str)
            return forex_rates

        return None

    @staticmethod
    def __parse_price_table(table_html):
        soup = BeautifulSoup(table_html, "html.parser")
        grade_price_dict = {}

        rows = soup.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 2:
                grade = cols[0].text.strip()
                price = float(cols[1].text.removeprefix("$").replace(",", "").strip())
                grade_price_dict[grade] = price

        return grade_price_dict

    @staticmethod
    def scrape_products(products: List[Product]) -> List[Product]:
        updated_products = []
        for product in products:
            try:
                updated_product = Scraper.scrape_product(product)
                updated_products.append(updated_product)
            except Exception as e:
                print(f"Error scraping product {product}: {e}")
                updated_products.append(product)  # keep original product if scraping fails
        return updated_products

    @staticmethod
    def scrape_product(product: Product) -> Product:
        response = requests.get(product.url, allow_redirects=False, timeout=5)
        if not response.ok:
            raise ConnectionError

        page_source = response.text
        soup = BeautifulSoup(page_source, "html.parser")

        script = soup.find("script", type="text/javascript").string
        forex_rates = Scraper.__extract_forex_rates(script)
        # TODO: do sumn with these rates

        card_title = soup.select_one("#product_name")
        product.name = collapse_spaces(card_title.text.replace("\n", "")) if card_title else "N/A"

        card_prices_table = soup.select_one("#full-prices table")
        prices = Scraper.__parse_price_table(str(card_prices_table)) if card_prices_table else "N/A"

        product.prices = prices

        return product
