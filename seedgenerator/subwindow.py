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
        
        enumList = list(q.getSettingEnumMap())
        enumList.append("New")
        self.enumModule = tuple(enumList)
        
        # window
        self.geometry("900x600")
        self.title("setting")
        
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
        
        # databaseFrame: Database config
        self.dbLabelFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.dbLabelFrame.pack(side=tk.TOP, fill="x")
        self.connectHostLabel = tk.Label(master=self.dbLabelFrame, text="Host", width=17)
        self.connectHostLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectSchemaLabel = tk.Label(master=self.dbLabelFrame, text="Schema", width=17)
        self.connectSchemaLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectUsernameLabel = tk.Label(master=self.dbLabelFrame, text="Username", width=17)
        self.connectUsernameLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectPasswordLabel = tk.Label(master=self.dbLabelFrame, text="Password", width=17)
        self.connectPasswordLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.dbFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.dbFrame.pack(side=tk.TOP, fill="x")
        self.connectHostEntry = tk.Entry(master=self.dbFrame, width=20)
        self.connectHostEntry.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectSchemaEntry = tk.Entry(master=self.dbFrame, width=20)
        self.connectSchemaEntry.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectUsernameEntry = tk.Entry(master=self.dbFrame, width=20)
        self.connectUsernameEntry.pack(side=tk.LEFT, padx=5, pady=5)
        self.connectPasswordEntry = tk.Entry(master=self.dbFrame, width=20)
        self.connectPasswordEntry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.dataBaseSettingButton = tk.Button(
            master=self.dbFrame,
            text="Setting",
            command=self.databaseSetting
        )
        self.dataBaseSettingButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        # separator
        self.separator = ttk.Separator(master=self.scrollable_frame, orient="horizontal")
        self.separator.pack(fill="both")
        
        # enum frame
        # top frame
        self.enumTopLabelFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.enumTopLabelFrame.pack(side=tk.TOP, fill="x")
        self.enumLabel = tk.Label(master=self.enumTopLabelFrame, text="Edit enum", width=17)
        self.enumLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.enumTopFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.enumTopFrame.pack(side=tk.TOP, fill="x")
        self.enumCombobox = ttk.Combobox(master=self.enumTopFrame, textvariable=tk.StringVar(), values=self.enumModule, style="office.TCombobox", width="17")
        self.enumCombobox.pack(side=tk.LEFT, padx=5, pady=5)
        
        # mid frame
        self.enumMidLabelFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.enumMidLabelFrame.pack(side=tk.TOP, fill="x")
        self.enumNameLabel = tk.Label(master=self.enumMidLabelFrame, text="Enum name", width=17)
        self.enumNameLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.enumMidFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.enumMidFrame.pack(side=tk.TOP, fill="x")
        self.enumNameEntry = tk.Entry(master=self.enumMidFrame, width=20)
        self.enumNameEntry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.enumSettingButton = tk.Button(
            master=self.enumMidFrame,
            text="Setting",
            command=self.enumSetting
        )
        self.enumSettingButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        # main frame
        self.enumMainLabelFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.enumMainLabelFrame.pack(side=tk.TOP, fill="x")
        
        self.enumParamLabel = tk.Label(master=self.enumMainLabelFrame, text="Parameter", width=17)
        self.enumParamLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.enumMainFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.enumMainFrame.pack(side=tk.TOP, fill="x")
        
        # widget manage parametar
        self.index = 0
        self.indexes = [] 
        self.frames = []
        self.insertEntries = []
        self.removeEntries = []
        
        # input enum parameter
        self.enumParamEntries = []
        
        self.createEntry(0)
    
    
    
    def insertEntry_click(self, event, id):
        next = self.indexes.index(id) + 1
        self.index = self.index + 1
        self.createEntry(next)
    
    # remove widget and wdget manager
    def removeEntry_click(self, event, id):
        current = self.indexes.index(id)

        self.enumParamEntries[current].destroy()
        self.insertEntries[current].destroy()
        self.removeEntries[current].destroy()
        self.frames[current].destroy()

        self.enumParamEntries.pop(current)
        self.insertEntries.pop(current)
        self.removeEntries.pop(current)
        self.frames.pop(current)
        self.indexes.pop(current)

        self.updateEntries()
        
    # widget pack
    def updateEntries(self):
        for i in range(len(self.indexes)):
            self.frames[i].pack(side=tk.TOP, fill="x")
            self.enumParamEntries[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.insertEntries[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.removeEntries[i].pack(side=tk.LEFT, padx=5, pady=5)

        if len(self.indexes) == 1:
            self.removeEntries[0].pack_forget()
    
    # widget create
    def createEntry(self, next):
        dataTypeList = []
        for e in d.InsertDataType:
            dataTypeList.append(e.value)
        dataTypeModule = tuple(dataTypeList)
        
        self.frames.insert(next, tk.Frame(self.enumMainFrame, width=100))
        self.enumParamEntries.insert(next, tk.Entry(self.frames[next], width=20))
        self.insertEntries.insert(next, tk.Label(
            self.frames[next],
            text="+",
            fg="#33ff33",
            font=("Arial Black", 20)
        ))
        self.removeEntries.insert(next, tk.Label(
            self.frames[next],
            text="-",
            fg="#ff3333",
            font=("Arial Black", 20)
        ))
        
        self.insertEntries[next].bind("<1>", lambda event, id=self.index: self.insertEntry_click(event, id))
        self.removeEntries[next].bind("<1>", lambda event, id=self.index: self.removeEntry_click(event, id))
        self.indexes.insert(next, self.index)
        self.updateEntries()
    
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
    
    def enumSetting(self):
        targetEnumName = self.enumCombobox.get()
        editEnumName = self.enumNameEntry.get()
        enumParamList = []
        for i in range(len(self.indexes)):
            enumParamList.append(self.enumParamEntries[i].get())
        try:
            q.settingEnumConfig(targetEnumName, editEnumName, enumParamList)
        except Exception as e:
            self.showAlertMessageBox(e.__class__.__name__, traceback.format_exc())