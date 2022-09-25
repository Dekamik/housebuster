import csv
import tkinter as tk
import tkinter.filedialog
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
            messagebox.showwarning("Restart program", "Crawler cannot run twice due to technical limitations.\n"
                                                      "Please restart the program to run again")
        self.results = []
        self.var_msg.set("Initializing, please wait...")
        self.update()

        location_ids = self.txt_loc_ids.text.get("1.0", tk.END)\
            .replace("\n", ",")\
            .replace(",,", ",")\
            .replace(", ", ",")\
            .strip()
        if location_ids[-1] == ",":
            location_ids = location_ids[:-1]

        if location_ids is None or len(location_ids) == 0:
            loc_ids = []
            for val in self.var_known_locations.values():
                if val.get() != 0:
                    loc_ids.append(str(val.get()))
            location_ids = ",".join(loc_ids)

        if location_ids is None or len(location_ids) == 0:
            messagebox.showwarning("Empty search", "Location IDs and Text search empty or invalid")
            self.var_msg.set(f"Ready")
            return

        self.save_crawler_settings(True)

        def crawler_results(signal, sender, item, response, spider):
            self.results.append(item)
            self.var_msg.set(f"Scraping item {len(self.results)}")
            self.update()

        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        self.has_been_run = True
        process = CrawlerProcess()
        process.crawl(HemnetSpider, ids=location_ids)
        process.start()

        if len(self.results) == 0:
            messagebox.showinfo("Scraping done", "No items found")
            self.var_msg.set("Ready")
            return

        self.sht_results.headers([column for column in self.results[0].keys()])
        self.sht_results.set_sheet_data([[column for column in row.values()] for row in self.results])

        self.btn_save["state"] = tk.NORMAL
        self.var_msg.set("Ready")
        messagebox.showinfo("Scraping done", f"Scraped {len(self.results)} items")

    def save_crawler_settings(self, supress_msg_box=False):
        self.config["crawler_settings"]["max_price"] = self.var_max_price.get()
        self.config["crawler_settings"]["price_mul"] = self.var_price_mul.get()
        self.config["crawler_settings"]["fee_mul"] = self.var_fee_mul.get()
        self.config["crawler_settings"]["size_mul"] = self.var_size_mul.get()
        self.config["crawler_settings"]["rooms_mul"] = self.var_rooms_mul.get()
        self.config["crawler_settings"]["balcony_pts"] = self.var_balcony_pts.get()
        self.config["crawler_settings"]["patio_pts"] = self.var_patio_pts.get()
        self.config["crawler_settings"]["highest_floor_pts"] = self.var_highest_floor_pts.get()
        self.config["crawler_settings"]["preferred_floor_pts"] = self.var_preferred_floor_pts.get()
        self.config["crawler_settings"]["preferred_floor"] = self.var_preferred_floor.get()
        self.config["crawler_settings"]["lowest_floor_pts"] = self.var_lowest_floor_pts.get()
        self.config["crawler_settings"]["elevator_pts"] = self.var_elevator_pts.get()
        self.config["crawler_settings"]["pts_adjust"] = self.var_pts_adjust.get()
        config.save(self.config)
        if not supress_msg_box:
            messagebox.showinfo("Saved", "Crawler settings saved")

    def save_crawler_results(self):
        with tkinter.filedialog.asksaveasfile(mode="w", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                                              defaultextension=".csv") as f:
            if f is None:
                return
            keys = self.results[0].keys()
            dw = csv.DictWriter(f, keys)
            dw.writeheader()
            dw.writerows(self.results)

    def select_known_location(self):
        selected_locations_amount = 0
        for val in self.var_known_locations.values():
            if val.get() != 0:
                selected_locations_amount += 1
        if selected_locations_amount != 0:
            self.var_known_locations_label.set(f"Known locations ({selected_locations_amount})")
        else:
            self.var_known_locations_label.set(f"Known locations")

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
        self.var_known_locations = {}
        self.var_known_locations_label = tk.StringVar(self, value="Known locations")
        self.var_max_price = tk.IntVar(self, value=crawler_settings["max_price"])
        self.var_price_mul = tk.DoubleVar(self, value=crawler_settings["price_mul"])
        self.var_fee_mul = tk.DoubleVar(self, value=crawler_settings["fee_mul"])
        self.var_size_mul = tk.DoubleVar(self, value=crawler_settings["size_mul"])
        self.var_rooms_mul = tk.DoubleVar(self, value=crawler_settings["rooms_mul"])
        self.var_balcony_pts = tk.IntVar(self, value=crawler_settings["balcony_pts"])
        self.var_patio_pts = tk.IntVar(self, value=crawler_settings["patio_pts"])
        self.var_highest_floor_pts = tk.IntVar(self, value=crawler_settings["highest_floor_pts"])
        self.var_preferred_floor_pts = tk.IntVar(self, value=crawler_settings["preferred_floor_pts"])
        self.var_preferred_floor = tk.StringVar(self, value=crawler_settings["preferred_floor"])
        self.var_lowest_floor_pts = tk.IntVar(self, value=crawler_settings["lowest_floor_pts"])
        self.var_elevator_pts = tk.IntVar(self, value=crawler_settings["elevator_pts"])
        self.var_pts_adjust = tk.IntVar(self, value=crawler_settings["pts_adjust"])

        self.var_msg = tk.StringVar(self)

        self.var_msg.set("Ready")

        # Components
        self.sht_results = tks.Sheet(self)
        frm_sidebar = tk.Frame(self, relief=tk.RAISED, bd=2)

        self.txt_loc_ids = entry.LabelledText(frm_sidebar, "Location IDs", 40, 4, 0, 1)

        lbl_known = tk.Label(frm_sidebar, textvariable=self.var_known_locations_label)
        mbn_known = tk.Menubutton(frm_sidebar, text="Select", relief=tk.RAISED)
        mbn_known.menu = tk.Menu(mbn_known, tearoff=0)
        mbn_known["menu"] = mbn_known.menu
        for loc in self.config["known_location_ids"].keys():
            self.var_known_locations[loc] = tk.IntVar(self)
            mbn_known.menu.add_checkbutton(label=loc, variable=self.var_known_locations[loc], offvalue=0,
                                           onvalue=self.config["known_location_ids"][loc],
                                           command=self.select_known_location)
        lbl_known.grid(row=2, column=0, sticky="e", padx=5, pady=5)
        mbn_known.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        entry.LabelledEntry(frm_sidebar, "Max price", self.var_max_price, 4)
        entry.LabelledEntry(frm_sidebar, "Price pts per kr", self.var_price_mul, 5)
        entry.LabelledEntry(frm_sidebar, "Fee pts per kr", self.var_fee_mul, 6)
        entry.LabelledEntry(frm_sidebar, "Size pts per m2", self.var_size_mul, 7)
        entry.LabelledEntry(frm_sidebar, "Pts per room", self.var_rooms_mul, 8)
        entry.LabelledEntry(frm_sidebar, "Balcony pts", self.var_balcony_pts, 9)
        entry.LabelledEntry(frm_sidebar, "Patio pts", self.var_patio_pts, 10)
        entry.LabelledEntry(frm_sidebar, "Highest floor pts", self.var_highest_floor_pts, 11)
        entry.LabelledEntry(frm_sidebar, "Preferred floor pts", self.var_preferred_floor_pts, 12)
        entry.LabelledEntry(frm_sidebar, "Preferred floor", self.var_preferred_floor, 13)
        entry.LabelledEntry(frm_sidebar, "Lowest floor pts", self.var_lowest_floor_pts, 14)
        entry.LabelledEntry(frm_sidebar, "Elevator pts", self.var_elevator_pts, 15)
        entry.LabelledEntry(frm_sidebar, "Final pts adjustment", self.var_pts_adjust, 16)

        self.btn_save_settings = tk.Button(frm_sidebar, text="Save Crawler Settings",
                                           command=self.save_crawler_settings)
        self.btn_crawl = tk.Button(frm_sidebar, text="Crawl", command=self.crawl)
        self.btn_save = tk.Button(frm_sidebar, text="Save Items As...", command=self.save_crawler_results)
        self.btn_save_settings.grid(row=17, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.btn_crawl.grid(row=18, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=18, column=1, sticky="ew", padx=5, pady=5)
        self.btn_save["state"] = tk.DISABLED

        frm_ribbon = tk.Frame(self)
        txt_messages = tk.Label(frm_ribbon, textvariable=self.var_msg)
        txt_messages.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        frm_sidebar.grid(row=0, column=0, sticky="ns")

        self.sht_results.grid(row=0, column=1, sticky="nsew")
        frm_ribbon.grid(row=1, column=0, columnspan=2, sticky="ws")


app = Program()
app.mainloop()
