"""
Written for hemnet.se 2022-09-14
"""
import unicodedata

import scrapy


def build_url(location_ids: list, item_types: list, price_max: int):
    location_id_params = "&".join([f"location_ids%5B%5D={location_id}" for location_id in location_ids])
    item_type_params = "&".join([f"item_types%5B%5D={item_type}" for item_type in item_types])
    return f"https://www.hemnet.se/bostader?{location_id_params}&{item_type_params}&price_max={price_max}"


class HouseSpider(scrapy.Spider):
    name = "housespider"

    def start_requests(self):
        urls = [
            build_url(["18042", "18028"], ["bostadsratt"], 2500000)     # Solna & Sundbyberg
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        count = len(response.css("li.js-normal-list-item"))

        for i in range(1, count):
            yield {
                "Adress": response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/div[2]/div/div[1]/div/h2/text()").get().strip(),
                "Område": response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/div[2]/div/div[1]/div/div/span[2]/text()").get().strip(),
                "Pris (kr)": unicodedata.normalize("NFKD", response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/div[2]/div/div[2]/div[1]/div[1]/text()").get()).replace("kr", "").strip().replace(" ", ""),
                "Yta (m2)": unicodedata.normalize("NFKD", response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/div[2]/div/div[2]/div[1]/div[2]/text()").get()).replace("m2", "").strip(),
                "Rum": unicodedata.normalize("NFKD", response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/div[2]/div/div[2]/div[1]/div[3]/text()").get()).replace("rum", "").strip(),
                "Avgift (kr/mån)": unicodedata.normalize("NFKD", response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/div[2]/div/div[2]/div[2]/div[1]/text()").get()).encode("ascii", "ignore").decode("utf-8").replace("kr/man", "").strip(),
                "Pris/kvm (kr/m2)": unicodedata.normalize("NFKD", response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/div[2]/div/div[2]/div[2]/div[2]/text()").get()).replace("kr/m2", "").strip(),
                "Länk": response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/@href").get().strip()
            }

        next_page = response.css("a.next_page::attr(href)").get()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse)
