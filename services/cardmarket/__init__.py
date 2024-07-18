import datetime
import os
import csv
from threading import Thread
from time import sleep
from typing import List, Optional, Dict, Any

import requests
from bs4 import BeautifulSoup


class Product:
    def __init__(self, url: str, name: Optional[str] = None, last_known_price: Optional[int] = None):
        self.url = url
        self.name = name
        self.last_known_price = last_known_price

    @staticmethod
    def from_dict(_dict: Dict[str, Any]) -> "Product":
        url = _dict.get("url")
        name = _dict.get("name")
        last_known_price = _dict.get("last_known_price")
        if last_known_price is not None:
            last_known_price = int(last_known_price)

        return Product(url, name, last_known_price)

    def __repr__(self):
        if self.last_known_price:
            return f"{self.name}: {self.last_known_price}"
        return self.name if self.name else f"UNKNOWN <{self.url}>"


class Tracker:
    def __init__(self, csv_listing_file: str, refresh_time_minutes: int):
        self.listing_file = csv_listing_file
        self.refresh_time_minutes = refresh_time_minutes
        self.products = []

        self.__last_tracked = None
        self.__stop_thread = False

    def load_products_from_listing_file(self) -> List[Product]:
        if not os.path.exists(self.listing_file):
            raise FileNotFoundError

        with open(self.listing_file) as listing_file:
            reader = csv.reader(listing_file)
            headers = next(reader, None)
            products = [Product.from_dict({header: item for (header, item) in zip(headers, row)}) for row in reader]

        return products

    def start(self) -> None:
        def run():
            while not self.__stop_thread:
                print("Refreshing product list...")

                self.products = self.load_products_from_listing_file()
                self.products = Scraper.scrape_products(self.products)
                self.__last_tracked = datetime.datetime.now()

                print(f"Products refreshed. Next refresh in {self.refresh_time_minutes} minutes.")
                sleep(self.refresh_time_minutes * 60)

        self.__stop_thread = False
        thread = Thread(target=run, daemon=False)
        thread.start()
        print("Price tracker started.")

    def stop(self) -> None:
        self.__stop_thread = True
        print("Price tracker stopped.")

    @property
    def running(self) -> bool:
        return not self.__stop_thread

    @property
    def last_tracked(self) -> datetime:
        return self.__last_tracked


class Scraper:
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

        card_title = soup.select_one(".page-title-container.d-flex.align-items-center.text-break")
        product.name = card_title.text

        card_last_price = soup.select_one("dd.col-6:nth-child(12)")
        product.last_known_price = float(card_last_price.text.replace(",", ".").split()[0])

        return product
