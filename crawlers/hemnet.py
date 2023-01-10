"""
Written for hemnet.se 2022-09-17
"""
import unicodedata

import scrapy

from crawlers import hemnet_analysis
from files import config


def build_url(location_ids: list, item_types: list, price_max: int) -> str:
    location_id_params = "&".join([f"location_ids%5B%5D={location_id}" for location_id in location_ids])
    item_type_params = "&".join([f"item_types%5B%5D={item_type}" for item_type in item_types])
    return f"https://www.hemnet.se/bostader?{location_id_params}&{item_type_params}&price_max={price_max}"


def parse_currency(raw, denomination) -> int:
    return int(unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("utf8").replace(denomination, "")
               .replace(" ", "").strip())


class HemnetSpider(scrapy.Spider):
    name = "hemnet"

    def __init__(self, ids=None, names=None, config_path=None, *args, **kwargs):
        super(HemnetSpider, self).__init__(*args, **kwargs)
        self.ids = ids
        self.names = names
        if config_path is not None:
            self.config = config.load(config_path)
        else:
            self.config = config.load()["crawler_settings"]

    def start_requests(self):
        urls = []
        if self.ids is not None and len(self.ids) != 0:
            for location_id in self.ids.split(","):
                urls.append(build_url([location_id], ["bostadsratt"], self.config["max_price"]))
        else:
            raise ValueError("ids must be set")

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

            analysis_settings = hemnet_analysis.FeatureAnalysisConfig(self.config["balcony_pts"],
                                                                      self.config["patio_pts"],
                                                                      self.config["highest_floor_pts"],
                                                                      self.config["preferred_floor_pts"],
                                                                      self.config["preferred_floor"],
                                                                      self.config["lowest_floor_pts"],
                                                                      self.config["elevator_pts"])

            price_pts = hemnet_analysis.get_price_pts(price, fee, self.config["price_mul"], self.config["fee_mul"])
            size_pts = hemnet_analysis.get_size_pts(size, rooms, self.config["size_mul"], self.config["rooms_mul"])
            features_pts = hemnet_analysis.get_features_pts(balcony, patio, floor, has_elevator, analysis_settings)
            total_pts = price_pts + size_pts + features_pts + self.config["pts_adjust"]

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
                "Poäng": int(total_pts),
                "Länk": response.url
            }

        except TypeError as e:
            pass
