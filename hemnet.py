"""
Written for hemnet.se 2022-09-17
"""
import unicodedata

import scrapy


def build_url(location_ids: list, item_types: list, price_max: int) -> str:
    location_id_params = "&".join([f"location_ids%5B%5D={location_id}" for location_id in location_ids])
    item_type_params = "&".join([f"item_types%5B%5D={item_type}" for item_type in item_types])
    return f"https://www.hemnet.se/bostader?{location_id_params}&{item_type_params}&price_max={price_max}"


def parse_currency(raw, denomination) -> int:
    return int(unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode("utf8").replace(denomination, "").replace(" ", "").strip())


def get_price_index(price, fee):
    price_idx = price / 1000
    fee_idx = fee / 5
    return price_idx + fee_idx


def get_size_index(size, rooms):
    size_idx = (100 - size) * 50
    room_idx = (2.5 - rooms) * 1000

    if rooms == 1:
        room_idx += 1000

    return size_idx + room_idx


def get_features_index(balcony, patio, floor, has_elevator):
    if balcony == "Ja":
        balcony_idx = 0
    else:
        balcony_idx = 1000

    if patio == "Ja":
        patio_idx = -400
    else:
        patio_idx = 200

    if floor[0:1] == floor[5:6]:
        floor_idx = -1500
        if has_elevator:
            floor_idx -= 500
    else:
        floor_idx = 0

    return balcony_idx + patio_idx + floor_idx


class HouseSpider(scrapy.Spider):
    name = "housespider"

    def start_requests(self):
        urls = [
            build_url(["18042", "18028"], ["bostadsratt"], 2500000),                        # Solna & Sundbyberg
            #build_url(["17853"], ["bostadsratt"], 2500000),                                 # Nacka
            build_url(["473337", "898740"], ["bostadsratt"], 2500000),                      # Alvik & Bromma
            build_url(["925961", "473424", "473365", "941046"], ["bostadsratt"], 2500000)   # Enskede, Stureby, Gubbängen, Enskede - Skarpnäck
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        count = len(response.css("li.js-normal-list-item"))
        for i in range(1, count):
            url = response.xpath(f"//li[contains(@class, 'js-normal-list-item')][{i}]/a/@href").get().strip()
            yield response.follow(url=url, callback=self.parse_detail)

        next_page = response.css("a.next_page::attr(href)").get()
        if next_page is not None:
            yield response.follow(url=next_page, callback=self.parse)

    def parse_detail(self, response):
        try:
            price = parse_currency(response.css("p.qa-property-price::text").get(), "kr")
            rooms = float(response.css("dd.property-attributes-table__value::text").re_first("^.+ rum").replace(" rum", "").replace(",", "."))
            size = float(response.css("dd.property-attributes-table__value::text").re_first("^.+ m²").replace(" m²", "").replace(",", "."))
            balcony = (response.xpath("//div[contains(@class, 'qa-balcony-attribute')]/dd/text()").get() or "Nej").strip()
            patio = (response.xpath("//div[contains(@class, 'qa-patio-attribute')]/dd/text()").get() or "Nej").strip()
            floor = (response.xpath("//div[contains(@class, 'qa-floor-attribute')]/dd/text()").get() or "?").strip()
            has_elevator = "hiss finns" in floor.lower() and "ej" not in floor.lower()
            fee = parse_currency(response.css("dd.property-attributes-table__value::text").re_first("^.+kr\/mån"), "kr/man")
            operational_costs = (parse_currency(response.css("dd.property-attributes-table__value::text").re_first("^.+kr\/år") or "-1", "kr/ar"))
            price_m2 = parse_currency(response.css("dd.property-attributes-table__value::text").re_first("^.+kr\/m²"), "kr/m2")
            price_idx = get_price_index(price, fee)
            size_idx = get_size_index(size, rooms)
            features_idx = get_features_index(balcony, patio, floor, has_elevator)
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
                "Prisindex": str(price_idx).replace(".", ","),
                "Storleksindex": str(size_idx).replace(".", ","),
                "Funktionsindex": str(features_idx).replace(".", ","),
                "Totalindex": str(total_idx).replace(".", ","),
                "Länk": response.url
            }

        except TypeError as e:
            pass
