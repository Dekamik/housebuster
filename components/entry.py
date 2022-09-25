import tkinter as tk


class LabelledEntry(tk.Frame):
    def __init__(self, parent, label, variable, row, lbl_col = 0, ent_col = 1):
        super().__init__(parent)
        self.label = tk.Label(parent, text=label)
        self.entry = tk.Entry(parent, textvariable=variable)
        self.label.grid(row=row, column=lbl_col, sticky="e", padx=5, pady=5)
        self.entry.grid(row=row, column=ent_col, sticky="w", padx=5, pady=5)
