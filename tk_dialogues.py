from tkinter import *
from tkinter import ttk
import pygame as pg


class EditMenu:
    def __init__(self, properties:dict):
        self.root = Tk()
        self.properties_var = {prop:StringVar(value=str(value)) for prop, value in properties.items()}
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True, padx=20, pady=20)

        frm.grid_columnconfigure(0, weight=1)
        ttk.Label(frm, text='Object Properties').grid(column=0, row=0, pady=2)
        rows = 1
        for prop in properties.keys():
            ttk.Label(frm, text=prop).grid(column=0, row=rows, sticky='ew')
            rows += 1
            ttk.Entry(frm, textvariable=self.properties_var[prop]).grid(column=0, row=rows, pady=2, sticky='ew')
            rows += 1
        ttk.Button(frm, text='Save', command=self.save).grid(column=0, row=rows+1, pady=2, sticky='ew')
        self.root.minsize(300, self.root.winfo_height())
        self.root.resizable(False, False)
        self.root.mainloop()
    
    def save(self):
        pg.event.post(pg.event.Event(pg.USEREVENT+2, {prop:string_var.get() for prop, string_var in self.properties_var.items()}))
        self.root.destroy()
