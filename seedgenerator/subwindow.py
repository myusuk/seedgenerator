#coding: utf-8
import tkinter as tk
from tkinter import messagebox
from tkinter import HORIZONTAL, N, S, E, W
from tkinter import ttk
from tkinter import filedialog
import threading
import traceback
from query_converter import QueryConverter as q
from enum import Enum
from define import Define as d

class SubWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        
        self.enumModule = tuple(q.getSettingEnumList())
        
        # window
        self.geometry("1300x600")
        self.title("seed generator")
        
        # canvas, scrollWindow, scrollBar
        self.canvas = tk.Canvas(self)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill="x")
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)
        
        # topFrame: Database config
        self.topLabelFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.topLabelFrame.pack(side=tk.TOP, fill="x")
        self.connectHostLabel = tk.Label(master=self.topLabelFrame, text="Host", width=17)
        self.connectHostLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectSchemaLabel = tk.Label(master=self.topLabelFrame, text="Schema", width=17)
        self.connectSchemaLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectUsernameLabel = tk.Label(master=self.topLabelFrame, text="Username", width=17)
        self.connectUsernameLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectPasswordLabel = tk.Label(master=self.topLabelFrame, text="Password", width=17)
        self.connectPasswordLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.topFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.topFrame.pack(side=tk.TOP, fill="x")
        self.connectHostEntry = tk.Entry(master=self.topFrame, width=20)
        self.connectHostEntry.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectSchemaEntry = tk.Entry(master=self.topFrame, width=20)
        self.connectSchemaEntry.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectUsernameEntry = tk.Entry(master=self.topFrame, width=20)
        self.connectUsernameEntry.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectPasswordEntry = tk.Entry(master=self.topFrame, width=20)
        self.connectPasswordEntry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.dataBaseSettingButton = tk.Button(
            master=self.topFrame,
            text="Setting",
            command=self.databaseSetting
        )
        self.dataBaseSettingButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        # separator
        self.separator = ttk.Separator(master=self.scrollable_frame, orient="horizontal")
        self.separator.pack(fill="both")
        
    def showAlertMessageBox(self, title, message):
        messagebox.showerror(title, message)
    
    def databaseSetting(self):
        host = self.connectHostEntry.get()
        schema = self.connectSchemaEntry.get()
        username = self.connectUsernameEntry.get()
        password = self.connectPasswordEntry.get()
        try:
            q.settingDatabaseConfig(host, schema, username, password)
        except Exception as e:
            self.showAlertMessageBox(e.__class__.__name__, traceback.format_exc())
        