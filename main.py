import tkinter as tk
from tkinter import messagebox

import tksheet as tks
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from components import entry
from crawlers.hemnet import HemnetSpider
from files import config


class Program(tk.Tk):
    def crawl(self):
        if self.has_been_run:
            messagebox.showerror("Restart program", "Crawler cannot run twice due to technical limitations.\n"
                                                    "Please restart the program to run again")

        self.results = []
        self.var_msg.set("Initializing, please wait...")

        search_text = self.txt_search.get("1.0", tk.END)\
            .replace("\n", ",")\
            .replace(",,", ",")\
            .replace(", ", ",")\
            .strip()
        if search_text[-1] == ",":
            search_text = search_text[:-1]

        self.save_crawler_settings(True)

        def crawler_results(signal, sender, item, response, spider):
            self.results.append(item)
            self.var_msg.set(f"Scraping item {len(self.results)}")
            self.update()

        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        self.has_been_run = True
        process = CrawlerProcess()
        process.crawl(HemnetSpider, names=search_text)
        process.start()

        self.sht_results.headers([column for column in self.results[0].keys()])
        self.sht_results.set_sheet_data([[column for column in row.values()] for row in self.results])

        self.btn_save["state"] = tk.NORMAL
        self.var_msg.set(f"Ready")
        messagebox.showinfo("Scraping done", f"Scraped {len(self.results)} items")

    def save_crawler_settings(self, supress_msg_box=False):
        self.config["crawler_settings"]["max_price"] = self.var_max_price.get()
        self.config["crawler_settings"]["price_mul"] = self.var_price_mul.get()
        self.config["crawler_settings"]["fee_mul"] = self.var_fee_mul.get()
        self.config["crawler_settings"]["size_mul"] = self.var_size_mul.get()
        self.config["crawler_settings"]["rooms_mul"] = self.var_rooms_mul.get()
        self.config["crawler_settings"]["balcony_bias"] = self.var_balcony_bias.get()
        self.config["crawler_settings"]["patio_bias"] = self.var_patio_bias.get()
        self.config["crawler_settings"]["highest_floor_bias"] = self.var_highest_floor_bias.get()
        self.config["crawler_settings"]["preferred_floor_bias"] = self.var_preferred_floor_bias.get()
        self.config["crawler_settings"]["preferred_floor"] = self.var_preferred_floor.get()
        self.config["crawler_settings"]["lowest_floor_bias"] = self.var_lowest_floor_bias.get()
        self.config["crawler_settings"]["elevator_bias"] = self.var_elevator_bias.get()
        config.save(self.config)
        if not supress_msg_box:
            messagebox.showinfo("Saved", "Crawler settings saved")

    def save_crawler_results(self):
        pass

    def __init__(self):
        tk.Tk.__init__(self)
        self.has_been_run = False

        # Configuration
        self.title("housebuster")
        self.rowconfigure(0, minsize=240, weight=1)
        self.columnconfigure(1, minsize=120, weight=1)

        self.config = config.load()

        crawler_settings = self.config["crawler_settings"]

        # Variables
        self.results = []
        self.var_search = tk.StringVar(self)
        self.var_max_price = tk.IntVar(self, value=crawler_settings["max_price"])
        self.var_price_mul = tk.DoubleVar(self, value=crawler_settings["price_mul"])
        self.var_fee_mul = tk.DoubleVar(self, value=crawler_settings["fee_mul"])
        self.var_size_mul = tk.DoubleVar(self, value=crawler_settings["size_mul"])
        self.var_rooms_mul = tk.DoubleVar(self, value=crawler_settings["rooms_mul"])
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
        self.txt_search = tk.Text(frm_sidebar, width=40, height=6)
        lbl_search.grid(row=0, column=0, columnspan=3, sticky="ns", padx=5, pady=5)
        self.txt_search.grid(row=1, column=0, columnspan=3, sticky="ns", padx=5, pady=5)

        entry.LabelledEntry(frm_sidebar, "Max price", self.var_max_price, 2)
        entry.LabelledEntry(frm_sidebar, "Price bias multiplier", self.var_price_mul, 3)
        entry.LabelledEntry(frm_sidebar, "Fee bias multiplier", self.var_fee_mul, 4)
        entry.LabelledEntry(frm_sidebar, "Size bias multiplier", self.var_size_mul, 5)
        entry.LabelledEntry(frm_sidebar, "Rooms bias multiplier", self.var_rooms_mul, 6)
        entry.LabelledEntry(frm_sidebar, "Balcony bias", self.var_balcony_bias, 7)
        entry.LabelledEntry(frm_sidebar, "Patio bias", self.var_patio_bias, 8)
        entry.LabelledEntry(frm_sidebar, "Highest floor bias", self.var_highest_floor_bias, 9)
        entry.LabelledEntry(frm_sidebar, "Preferred floor bias", self.var_preferred_floor_bias, 10)
        entry.LabelledEntry(frm_sidebar, "Preferred floor", self.var_preferred_floor, 11)
        entry.LabelledEntry(frm_sidebar, "Lowest floor bias", self.var_lowest_floor_bias, 12)
        entry.LabelledEntry(frm_sidebar, "Elevator bias", self.var_elevator_bias, 13)

        self.btn_save_settings = tk.Button(frm_sidebar, text="Save Crawler Settings", command=self.save_crawler_settings)
        self.btn_crawl = tk.Button(frm_sidebar, text="Crawl", command=self.crawl)
        self.btn_save = tk.Button(frm_sidebar, text="Save Items As...")
        self.btn_save_settings.grid(row=14, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.btn_crawl.grid(row=15, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=15, column=1, sticky="ew", padx=5, pady=5)
        self.btn_save["state"] = tk.DISABLED

        frm_ribbon = tk.Frame(self)
        txt_messages = tk.Label(frm_ribbon, textvariable=self.var_msg)
        txt_messages.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        frm_sidebar.grid(row=0, column=0, sticky="ns")

        self.sht_results.grid(row=0, column=1, sticky="nsew")
        frm_ribbon.grid(row=1, column=0, columnspan=2, sticky="ws")


app = Program()
app.mainloop()
