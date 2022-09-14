"""
Written for hemnet.se 2022-09-14
"""
from dataclasses import dataclass

import scrapy


def get_url(location_ids: list, item_types: list, price_max: int):
    location_id_params = "&".join([f"location_ids%5B%5D={location_id}" for location_id in location_ids])
    item_type_params = "&".join([f"item_types%5B%5D={item_type}" for item_type in item_types])
    return f"https://www.hemnet.se/bostader?{location_id_params}&{item_type_params}&price_max={price_max}"


@dataclass
class HouseData:
    headers = "Adress;Område;Storlek;Rum;Pris;Avgift;Pris/kvm;Länk"
    address: str
    neighborhood: str
    size: int           # m^2
    rooms: float        # rum
    price: int          # kr
    fee: int            # kr/mån
    price_sqr_ft: int   # kr/m^2
    url: str

    def __str__(self):
        return ";".join([self.address, self.neighborhood, str(self.size), str(self.rooms), str(self.price),
                         str(self.fee), str(self.price_sqr_ft), self.url])


class HouseSpider(scrapy.Spider):
    name = "housespider"

    def start_requests(self):
        urls = [
            get_url(["18042", "18028"], ["bostadsratt"], 2500000)  # Solna & Sundbyberg
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        next_page = response.css("a.next_page::attr(href)").get()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse)
