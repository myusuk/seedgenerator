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
       

