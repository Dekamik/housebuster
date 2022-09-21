import tkinter as tk

import tksheet as tks
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from crawlers.hemnet import HemnetSpider


class Program(tk.Tk):
    def crawl(self):
        self.results = []
        self.btn_crawl["state"] = tk.DISABLED
        self.var_msg.set("Initializing, please wait...")
        self.update()

        parsed_search_text = self.txt_search.get("1.0", tk.END)\
            .replace(" ", "")\
            .replace("\n", ",")\
            .replace(",,", ",")
        if parsed_search_text[-1] == ",":
            parsed_search_text = parsed_search_text[:-1]

        try:
            parsed_max_price = self.var_max_price.get()
            if parsed_max_price == 0:
                self.var_msg.set(f"ERROR: Max price cannot be 0")
                self.btn_crawl["state"] = tk.NORMAL
                return
        except tk.TclError as e:
            self.var_msg.set(f"ERROR: Max price {e}")
            self.btn_crawl["state"] = tk.NORMAL
            return

        def crawler_results(signal, sender, item, response, spider):
            self.results.append(item)
            self.var_msg.set(f"Scraping item {len(self.results)}")
            self.update()

        dispatcher.connect(crawler_results, signal=signals.item_scraped)

        process = CrawlerProcess()
        process.crawl(HemnetSpider, names=parsed_search_text, max_price=parsed_max_price)
        process.start()

        self.sht_results.headers([column for column in self.results[0].keys()])
        self.sht_results.set_sheet_data([[column for column in row.values()] for row in self.results])

        self.btn_save["state"] = tk.NORMAL
        self.var_msg.set(f"Scraped {len(self.results)} items")

    def __init__(self):
        tk.Tk.__init__(self)

        # Configuration
        self.title("housebuster")
        self.rowconfigure(0, minsize=240, weight=1)
        self.columnconfigure(1, minsize=120, weight=1)

        # Variables
        self.results = []
        self.var_search = tk.StringVar(self)
        self.var_max_price = tk.IntVar(self)
        self.var_msg = tk.StringVar(self)
        self.var_crawl_log = tk.StringVar(self)

        self.var_msg.set("Ready")

        # Components
        self.sht_results = tks.Sheet(self)
        frm_sidebar = tk.Frame(self, relief=tk.RAISED, bd=2)

        frm_define = tk.Frame(frm_sidebar)

        frm_search = tk.Frame(frm_define)
        lbl_search = tk.Label(frm_search, text="Search")
        self.txt_search = tk.Text(frm_search, width=30, height=10)
        lbl_search.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        self.txt_search.grid(row=1, column=0, sticky="ns", padx=5, pady=5)

        frm_max_price = tk.Label(frm_define)
        lbl_max_price = tk.Label(frm_max_price, text="Max price")
        ent_max_price = tk.Entry(frm_max_price, textvariable=self.var_max_price)
        lbl_max_price.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        ent_max_price.grid(row=0, column=1, sticky="ns", padx=5, pady=5)

        frm_buttons = tk.Frame(frm_sidebar)
        self.btn_crawl = tk.Button(frm_buttons, text="Crawl", command=self.crawl)
        self.btn_save = tk.Button(frm_buttons, text="Save As...")
        self.btn_crawl.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.btn_save.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.btn_save["state"] = tk.DISABLED

        frm_ribbon = tk.Frame(self)
        txt_messages = tk.Label(frm_ribbon, textvariable=self.var_msg)
        txt_messages.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        frm_sidebar.grid(row=0, column=0, sticky="ns")

        frm_define.grid(row=0, column=0, sticky="n", pady=10)
        frm_search.grid(row=2, column=0, sticky="ew", pady=5)
        frm_max_price.grid(row=4, column=0, sticky="ew", pady=5)

        frm_buttons.grid(row=1, column=0, sticky="s", pady=10)
        self.sht_results.grid(row=0, column=1, sticky="nsew")
        frm_ribbon.grid(row=1, column=0, columnspan=2, sticky="ws")


app = Program()
app.mainloop()
