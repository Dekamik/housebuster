"""
Written for hemnet.se 2022-09-17
"""
import unicodedata

import scrapy

from crawlers import hemnet_analysis
from files import config

hemnet_known_location_ids = {
    "bromma": "898740",
    "enskede": "925961",
    "enskede-skarpnäck": "941046",
    "gubbängen": "473365",
    "nacka": "17853",
    "solna": "18028",
    "stureby": "473424",
    "sundbyberg": "18042"
}


def build_url(location_ids: list, item_types: list, price_max: int) -> str:
    location_id_params = "&".join([f"location_ids%5B%5D={location_id}" for location_id in location_ids])
    item_type_params = "&".join([f"item_types%5B%5D={item_type}" for item_type in item_types])
    return f"https://www.hemnet.se/bostader?{location_id_params}&{item_type_params}&price_max={price_max}"


def parse_currency(raw, denomination) -> int:
    return int(unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("utf8").replace(denomination, "")
               .replace(" ", "").strip())


class HemnetSpider(scrapy.Spider):
    name = "housespider"

    def __init__(self, ids=None, names=None, *args, **kwargs):
        super(HemnetSpider, self).__init__(*args, **kwargs)
        self.ids = ids
        self.names = names
        self.config = config.load()["crawler_settings"]

    def start_requests(self):
        urls = []
        if self.ids is not None:
            for location_id in self.ids.split(","):
                urls.append(build_url([location_id], ["bostadsratt"], self.config["max_price"]))
        elif self.names is not None:
            for name in self.names.split(","):
                urls.append(build_url([hemnet_known_location_ids[name]], ["bostadsratt"], self.config["max_price"]))
        else:
            for location_id in hemnet_known_location_ids.values():
                urls.append(build_url([location_id], ["bostadsratt"], self.config["max_price"]))

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        count = len(response.css("li.js-normal-list-item"))
        for i in range(1, count):
            url = response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/@href").get()
            yield response.follow(url=url, callback=self.parse_detail)

        next_page = response.css("a.next_page::attr(href)").get()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_detail(self, response):
        try:
            price = parse_currency(response.css("p.qa-property-price::text").get(), "kr")
            rooms = float(response.css("dd.property-attributes-table__value::text").re_first("^.+ rum")
                          .replace(" rum", "").replace(",", "."))
            size = float(response.css("dd.property-attributes-table__value::text").re_first("^.+ m²")
                         .replace(" m²", "").replace(",", "."))
            balcony = (response.xpath("//div[contains(@class, 'qa-balcony-attribute')]/dd/text()").get() or "Nej")\
                .strip()
            patio = (response.xpath("//div[contains(@class, 'qa-patio-attribute')]/dd/text()").get() or "Nej").strip()
            floor = (response.xpath("//div[contains(@class, 'qa-floor-attribute')]/dd/text()").get() or "?").strip()
            has_elevator = "hiss finns" in floor.lower() and "ej" not in floor.lower()
            fee = parse_currency(response.css("dd.property-attributes-table__value::text")
                                 .re_first("^.+kr\/mån"), "kr/man")
            operational_costs = (parse_currency(response.css("dd.property-attributes-table__value::text")
                                                .re_first("^.+kr\/år") or "-1", "kr/ar"))
            price_m2 = parse_currency(response.css("dd.property-attributes-table__value::text")
                                      .re_first("^.+kr\/m²"), "kr/m2")

            analysis_settings = hemnet_analysis.FeatureAnalysisConfig(self.config["balcony_bias"],
                                                                      self.config["patio_bias"],
                                                                      self.config["highest_floor_bias"],
                                                                      self.config["preferred_floor_bias"],
                                                                      self.config["preferred_floor"],
                                                                      self.config["lowest_floor_bias"],
                                                                      self.config["elevator_bias"])

            # Indices - The lower the number, the better
            price_idx = hemnet_analysis.get_price_index(price, fee, self.config["price_mul"], self.config["fee_mul"])
            size_idx = hemnet_analysis.get_size_index(size, rooms, self.config["size_mul"], self.config["rooms_mul"])
            features_idx = hemnet_analysis.get_features_index(balcony, patio, floor, has_elevator, analysis_settings)
            total_idx = price_idx + size_idx + features_idx

            yield {
                "Adress": response.xpath("//h1[contains(@class, 'qa-property-heading')]/text()").get(),
                "Område": response.xpath("//span[contains(@class, 'property-address__area')]/text()").get(),
                "Pris": price,
                "Antal rum": rooms,
                "Boarea": size,
                "Balkong": balcony,
                "Uteplats": patio,
                "Våning": floor,
                "Har hiss": has_elevator,
                "Byggår": "",
                "Förening": response.xpath(
                    "//div[contains(@class, 'property-attributes-table__housing-cooperative-name')]/span/text()").get(),
                "Avgift": fee,
                "Driftkostnad": operational_costs,
                "Pris/m2": price_m2,
                "Index": total_idx,
                "Länk": response.url
            }

        except TypeError as e:
            pass
