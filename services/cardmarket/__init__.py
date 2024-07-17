import os.path
import csv
from typing import List, Optional, Dict, Any


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
    def __init__(self, csv_listing_file: str):
        self.listing_file = csv_listing_file
        self.products = Tracker.get_products_from_listing_file(csv_listing_file)

    @staticmethod
    def get_products_from_listing_file(csv_listing_file: str) -> List[Product]:
        if not os.path.exists(csv_listing_file):
            raise FileNotFoundError

        products = []
        with open(csv_listing_file) as listing_file:
            reader = csv.reader(listing_file)
            headers = next(reader, None)
            products = [Product.from_dict({header: item for (header, item) in zip(headers, row)}) for row in reader]

        return products


class Scraper:
    def __init__(self, products: List[Product]):
        self.products = products
