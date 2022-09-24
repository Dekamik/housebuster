import time
import tkinter as tk
from tkinter import messagebox

import yaml
import tksheet as tks
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from crawlers.hemnet import HemnetSpider


class Program(tk.Tk):
    def crawl(self):
        self.results = []
        self.var_msg.set("Initializing, please wait...")

        parsed_search_text = self.txt_search.get("1.0", tk.END)\
            .replace(" ", "")\
            .replace("\n", ",")\
            .replace(",,", ",")
        if parsed_search_text[-1] == ",":
            parsed_search_text = parsed_search_text[:-1]

        try:
            parsed_max_price = self.var_max_price.get()
            if parsed_max_price == 0:
                self.var_msg.set("ERROR: Max price cannot be 0")
                return
        except tk.TclError as e:
            self.var_msg.set(f"ERROR: Max price {e}")
            return

        def crawler_results(signal, sender, item, response, spider):
            self.results.append(item)
            self.var_msg.set(f"Scraping item {len(self.results)}")
            self.update()

        self.btn_crawl["state"] = tk.DISABLED
        self.update()

        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        process = CrawlerProcess()
        process.crawl(HemnetSpider, names=parsed_search_text, max_price=parsed_max_price)
        process.start()

        self.sht_results.headers([column for column in self.results[0].keys()])
        self.sht_results.set_sheet_data([[column for column in row.values()] for row in self.results])

        self.btn_save["state"] = tk.NORMAL
        self.var_msg.set(f"Ready")
        messagebox.showinfo("Scraping done", f"Scraped {len(self.results)} items")

    def save_crawler_settings(self):
        self.config["crawler_settings"]["max_price"] = self.var_max_price.get()
        self.config["crawler_settings"]["price_mul"] = self.var_price_mul.get()
        self.config["crawler_settings"]["fee_mul"] = self.var_fee_mul.get()
        self.config["crawler_settings"]["balcony_bias"] = self.var_balcony_bias.get()
        self.config["crawler_settings"]["patio_bias"] = self.var_patio_bias.get()
        self.config["crawler_settings"]["highest_floor_bias"] = self.var_highest_floor_bias.get()
        self.config["crawler_settings"]["preferred_floor_bias"] = self.var_preferred_floor_bias.get()
        self.config["crawler_settings"]["preferred_floor"] = self.var_preferred_floor.get()
        self.config["crawler_settings"]["lowest_floor_bias"] = self.var_lowest_floor_bias.get()
        self.config["crawler_settings"]["elevator_bias"] = self.var_elevator_bias.get()

        with open("config.yml", "w") as stream:
            yaml.safe_dump(self.config, stream)

        messagebox.showinfo("Saved", "Crawler settings saved")

    def __init__(self):
        tk.Tk.__init__(self)

        # Configuration
        self.title("housebuster")
        self.rowconfigure(0, minsize=240, weight=1)
        self.columnconfigure(1, minsize=120, weight=1)

        with open("config.yml", "r") as stream:
            self.config = yaml.safe_load(stream)

        crawler_settings = self.config["crawler_settings"]

        # Variables
        self.results = []
        self.var_search = tk.StringVar(self)
        self.var_max_price = tk.IntVar(self, value=crawler_settings["max_price"])
        self.var_price_mul = tk.DoubleVar(self, value=crawler_settings["price_mul"])
        self.var_fee_mul = tk.DoubleVar(self, value=crawler_settings["fee_mul"])
        self.var_balcony_bias = tk.IntVar(self, value=crawler_settings["balcony_bias"])
        self.var_patio_bias = tk.IntVar(self, value=crawler_settings["patio_bias"])
        self.var_highest_floor_bias = tk.IntVar(self, value=crawler_settings["highest_floor_bias"])
        self.var_preferred_floor_bias = tk.IntVar(self, value=crawler_settings["preferred_floor_bias"])
        self.var_preferred_floor = tk.StringVar(self, value=crawler_settings["preferred_floor"])
        self.var_lowest_floor_bias = tk.IntVar(self, value=crawler_settings["lowest_floor_bias"])
        self.var_elevator_bias = tk.IntVar(self, value=crawler_settings["elevator_bias"])

        self.var_msg = tk.StringVar(self)
        self.var_crawl_log = tk.StringVar(self)

        self.var_msg.set("Ready")

        # Components
        self.sht_results = tks.Sheet(self)
        frm_sidebar = tk.Frame(self, relief=tk.RAISED, bd=2)

        lbl_search = tk.Label(frm_sidebar, text="Search")
        self.txt_search = tk.Text(frm_sidebar, width=30, height=10)
        lbl_search.grid(row=0, column=0, columnspan=3, sticky="ns", padx=5, pady=5)
        self.txt_search.grid(row=1, column=0, columnspan=3, sticky="ns", padx=5, pady=5)

        lbl_max_price = tk.Label(frm_sidebar, text="Max price")
        ent_max_price = tk.Entry(frm_sidebar, textvariable=self.var_max_price)
        lbl_max_price.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ent_max_price.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        lbl_price_mul = tk.Label(frm_sidebar, text="Price bias multiplier")
        ent_price_mul = tk.Entry(frm_sidebar, textvariable=self.var_price_mul)
        lbl_price_mul.grid(row=3, column=0, sticky="e", padx=5, pady=5)
        ent_price_mul.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        lbl_fee_mul = tk.Label(frm_sidebar, text="Fee bias multiplier")
        ent_fee_mul = tk.Entry(frm_sidebar, textvariable=self.var_fee_mul)
        lbl_fee_mul.grid(row=4, column=0, sticky="e", padx=5, pady=5)
        ent_fee_mul.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        lbl_balcony = tk.Label(frm_sidebar, text="Balcony bias")
        ent_balcony = tk.Entry(frm_sidebar, textvariable=self.var_balcony_bias)
        lbl_balcony.grid(row=5, column=0, sticky="e", padx=5, pady=5)
        ent_balcony.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        lbl_patio = tk.Label(frm_sidebar, text="Patio bias")
        ent_patio = tk.Entry(frm_sidebar, textvariable=self.var_patio_bias)
        lbl_patio.grid(row=6, column=0, sticky="e", padx=5, pady=5)
        ent_patio.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        lbl_highest_floor = tk.Label(frm_sidebar, text="Highest floor bias")
        ent_highest_floor = tk.Entry(frm_sidebar, textvariable=self.var_highest_floor_bias)
        lbl_highest_floor.grid(row=7, column=0, sticky="e", padx=5, pady=5)
        ent_highest_floor.grid(row=7, column=1, sticky="w", padx=5, pady=5)

        lbl_preferred_floor = tk.Label(frm_sidebar, text="Preferred floor bias")
        ent_preferred_floor = tk.Entry(frm_sidebar, textvariable=self.var_preferred_floor_bias)
        lbl_preferred_floor.grid(row=8, column=0, sticky="e", padx=5, pady=5)
        ent_preferred_floor.grid(row=8, column=1, sticky="w", padx=5, pady=5)

        lbl_floor = tk.Label(frm_sidebar, text="Preferred floor")
        ent_floor = tk.Entry(frm_sidebar, textvariable=self.var_preferred_floor)
        lbl_floor.grid(row=9, column=0, sticky="e", padx=5, pady=5)
        ent_floor.grid(row=9, column=1, sticky="w", padx=5, pady=5)

        lbl_lowest_floor = tk.Label(frm_sidebar, text="Lowest floor bias")
        ent_lowest_floor = tk.Entry(frm_sidebar, textvariable=self.var_lowest_floor_bias)
        lbl_lowest_floor.grid(row=10, column=0, sticky="e", padx=5, pady=5)
        ent_lowest_floor.grid(row=10, column=1, sticky="w", padx=5, pady=5)

        lbl_elevator = tk.Label(frm_sidebar, text="Elevator bias")
        ent_elevator = tk.Entry(frm_sidebar, textvariable=self.var_elevator_bias)
        lbl_elevator.grid(row=11, column=0, sticky="e", padx=5, pady=5)
        ent_elevator.grid(row=11, column=1, sticky="w", padx=5, pady=5)

        self.btn_save_settings = tk.Button(frm_sidebar, text="Save Crawler Settings", command=self.save_crawler_settings)
        self.btn_crawl = tk.Button(frm_sidebar, text="Crawl", command=self.crawl)
        self.btn_save = tk.Button(frm_sidebar, text="Save Items As...")
        self.btn_save_settings.grid(row=12, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.btn_crawl.grid(row=13, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=13, column=1, sticky="ew", padx=5, pady=5)
        self.btn_save["state"] = tk.DISABLED

        frm_ribbon = tk.Frame(self)
        txt_messages = tk.Label(frm_ribbon, textvariable=self.var_msg)
        txt_messages.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        frm_sidebar.grid(row=0, column=0, sticky="ns")

        self.sht_results.grid(row=0, column=1, sticky="nsew")
        frm_ribbon.grid(row=1, column=0, columnspan=2, sticky="ws")


app = Program()
app.mainloop()
