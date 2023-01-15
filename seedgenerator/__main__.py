#coding: utf-8
import tkinter as tk
from tkinter import messagebox
from tkinter import HORIZONTAL, N, S, E, W
from tkinter import ttk
import threading
from query_converter import QueryConverter as q
from enum import Enum
from define import Define as d

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # window
        self.geometry('1300x600')
        self.title('seed generator')
        
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
        
        # topFrame: insertTableName, insertRecordLength, exportButton, executeButton
        self.topLabelFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.topLabelFrame.pack(side=tk.TOP, fill="x")
        self.insertTableNameLabel = tk.Label(master=self.topLabelFrame, text='Insert table name', width=17)
        self.insertTableNameLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.insertRecordLengthLabel = tk.Label(master=self.topLabelFrame, text='Insert column length', width=17)
        self.insertRecordLengthLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.topFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.topFrame.pack(side=tk.TOP, fill="x")
        self.insertTableNameEntry = tk.Entry(master=self.topFrame, width=20)
        self.insertTableNameEntry.pack(side=tk.LEFT, padx=5, pady=5)
        self.insertRecordLengthEntry = tk.Entry(master=self.topFrame, width=20)
        self.insertRecordLengthEntry.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.exportButton = tk.Button(
            master=self.topFrame,
            text='Export',
            command=lambda:self.startThread(self.exportQuery)
        )
        self.exportButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.executeButton = tk.Button(
            master=self.topFrame,
            text='Execute',
            command=lambda:self.showMessageBox(True, "Confirmation", "Really excute insert query?", self.excuteQuery)
        )
        self.executeButton.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.pb = ttk.Progressbar(
            self.topFrame,
            orient=HORIZONTAL,
            maximum=10,
            value=0,
            length=200,
            mode='indeterminate')
        
        # mine label frame
        self.mainLabelFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.mainLabelFrame.pack(side=tk.TOP, fill="x")
        
        self.insertColumnNameLabel = tk.Label(master=self.mainLabelFrame, text='Insert column name', width=17)
        self.insertColumnNameLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.dataTypeLabel = tk.Label(master=self.mainLabelFrame, text='Data type', width=17)
        self.dataTypeLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.selectTableNameLabel = tk.Label(master=self.mainLabelFrame, text='Select table name', width=17)
        self.selectTableNameLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.selectColumnNameLabel = tk.Label(master=self.mainLabelFrame, text='Select column name', width=17)
        self.selectColumnNameLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.enumNameLabel = tk.Label(master=self.mainLabelFrame, text='Enum name', width=17)
        self.enumNameLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.fixParamLabel = tk.Label(master=self.mainLabelFrame, text='Fix param', width=17)
        self.fixParamLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.serialStartNumberLabel = tk.Label(master=self.mainLabelFrame, text='Serial start number', width=17)
        self.serialStartNumberLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.inNullAbleLabel = tk.Label(master=self.mainLabelFrame, text='Null contain', width=10)
        self.inNullAbleLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.isBlankAbleLabel = tk.Label(master=self.mainLabelFrame, text='Blank contain', width=10)
        self.isBlankAbleLabel.pack(side=tk.LEFT, padx=5, pady=5)
        self.needQuoteLabel = tk.Label(master=self.mainLabelFrame, text='Need quote', width=10)
        self.needQuoteLabel.pack(side=tk.LEFT, padx=5, pady=5)
        
        # mainFrame: other input element
        self.mainFrame = tk.Frame(master=self.scrollable_frame, width=100)
        self.mainFrame.pack(side=tk.TOP, fill="x")
        
        # widget manage parametar
        self.index = 0
        self.indexes = [] 
        self.frames = []
        self.insertEntries = []
        self.removeEntries = []
        self.isNullBoolList = []
        self.isBlankBoolList = []
        self.needQuoteBoolList = []
        
        # input element field
        self.insertColumnNameEntries = []
        self.dataTypeComboboxes = []
        self.selectTableNameEntries = []
        self.selectColumnNameEntries = []
        self.enumNameComboboxes = []
        self.fixParamEntries = []
        self.serialStartNumberEntries = []
        self.isNullAbleCkButtons = []
        self.isBlankAbleCkButtons = []
        self.needQuoteCkButtons = []
        
        self.createEntry(0)
    
    def insertEntry_click(self, event, id):
        next = self.indexes.index(id) + 1
        self.index = self.index + 1
        self.createEntry(next)
    
    def removeEntry_click(self, event, id):
        current = self.indexes.index(id)

        self.insertColumnNameEntries[current].destroy()
        self.dataTypeComboboxes[current].destroy()
        self.selectTableNameEntries[current].destroy()
        self.selectColumnNameEntries[current].destroy()
        self.enumNameComboboxes[current].destroy()
        self.fixParamEntries[current].destroy()
        self.serialStartNumberEntries[current].destroy()
        self.isNullAbleCkButtons[current].destroy()
        self.isBlankAbleCkButtons[current].destroy()
        self.needQuoteCkButtons[current].destroy()
        self.insertEntries[current].destroy()
        self.removeEntries[current].destroy()
        self.frames[current].destroy()

        self.insertColumnNameEntries.pop(current)
        self.dataTypeComboboxes.pop(current)
        self.selectTableNameEntries.pop(current)
        self.selectColumnNameEntries.pop(current)
        self.enumNameComboboxes.pop(current)
        self.fixParamEntries.pop(current)
        self.serialStartNumberEntries.pop(current)
        self.isNullAbleCkButtons.pop(current)
        self.isBlankAbleCkButtons.pop(current)
        self.needQuoteCkButtons.pop(current)
        self.insertEntries.pop(current)
        self.removeEntries.pop(current)
        self.frames.pop(current)
        self.indexes.pop(current)
        
        self.isNullBoolList.pop(current)
        self.isBlankBoolList.pop(current)
        self.needQuoteBoolList.pop(current)

        self.updateEntries()
        
    # need edit
    def updateEntries(self):
        for i in range(len(self.indexes)):
            self.frames[i].pack(side=tk.TOP, fill="x")
            self.insertColumnNameEntries[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.dataTypeComboboxes[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.selectTableNameEntries[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.selectColumnNameEntries[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.enumNameComboboxes[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.fixParamEntries[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.serialStartNumberEntries[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.isNullAbleCkButtons[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.isBlankAbleCkButtons[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.needQuoteCkButtons[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.insertEntries[i].pack(side=tk.LEFT, padx=5, pady=5)
            self.removeEntries[i].pack(side=tk.LEFT, padx=5, pady=5)

        if len(self.indexes) == 1:
            self.removeEntries[0].pack_forget()
    
    # need edit
    def createEntry(self, next):
        dataTypeList = []
        for e in d.InsertDataType:
            dataTypeList.append(e.value)
        dataTypeModule = tuple(dataTypeList)
        
        self.isNullBoolList.insert(next, tk.BooleanVar())
        self.isBlankBoolList.insert(next, tk.BooleanVar())
        self.needQuoteBoolList.insert(next, tk.BooleanVar())
        
        enumModule = ()
        
        self.frames.insert(next, tk.Frame(self.mainFrame, width=100))
        self.insertColumnNameEntries.insert(next, tk.Entry(self.frames[next], width=20))
        self.dataTypeComboboxes.insert(next, ttk.Combobox(self.frames[next], textvariable=tk.StringVar(), values=dataTypeModule, style="office.TCombobox", width="17"))
        self.selectTableNameEntries.insert(next, tk.Entry(self.frames[next], width=20))
        self.selectColumnNameEntries.insert(next, tk.Entry(self.frames[next], width=20))
        self.enumNameComboboxes.insert(next, ttk.Combobox(self.frames[next], textvariable=tk.StringVar(), values=enumModule, style="office.TCombobox", width="17"))
        self.fixParamEntries.insert(next, tk.Entry(self.frames[next], width=20))
        self.serialStartNumberEntries.insert(next, tk.Entry(self.frames[next], width=20))
        self.isNullAbleCkButtons.insert(next, tk.Checkbutton(self.frames[next], variable=self.isNullBoolList[next], width=7))
        self.isBlankAbleCkButtons.insert(next, tk.Checkbutton(self.frames[next], variable=self.isBlankBoolList[next], width=7))
        self.needQuoteCkButtons.insert(next, tk.Checkbutton(self.frames[next], variable=self.needQuoteBoolList[next], width=7))
        self.insertEntries.insert(next, tk.Label(
            self.frames[next],
            text='+',
            fg='#33ff33',
            font=('Arial Black', 20)
        ))
        self.removeEntries.insert(next, tk.Label(
            self.frames[next],
            text='-',
            fg='#ff3333',
            font=('Arial Black', 20)
        ))
        
        self.insertEntries[next].bind('<1>', lambda event, id=self.index: self.insertEntry_click(event, id))
        self.removeEntries[next].bind('<1>', lambda event, id=self.index: self.removeEntry_click(event, id))
        self.indexes.insert(next, self.index)
        self.updateEntries()

    def showMessageBox(self, needThread, title, message, targetFunc):
        ret = messagebox.askokcancel(title, message)
        if ret:
            if needThread:
                self.startThread(targetFunc)
            targetFunc()
    
    def startThread(self, targetFunc):
        t = threading.Thread(target=targetFunc) 
        t.start() 
        
    def exportQuery(self):
        self.pb.pack(side=tk.LEFT)
        self.pb.start()
        
        query = self.getQuery()
        print(query)
        
        self.pb.stop()
        self.pb.pack_forget()
    
    def excuteQuery(self):
        self.pb.pack(side=tk.LEFT)
        self.pb.start()
        
        query = self.getQuery()
        
        self.pb.stop()
        self.pb.pack_forget()
        
    def getQuery(self):
        insertTableName = self.insertTableNameEntry.get()
        insertRecordLength = int(self.insertRecordLengthEntry.get())
        
        insertDataMapList = []
        for i in range(len(self.indexes)):
            insertDataMap = {}
            insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value] = self.insertColumnNameEntries[i].get()
            insertDataMap[d.InsertParam.DATA_TYPE.value] = self.dataTypeComboboxes[i].get()
            insertDataMap[d.InsertParam.SELECT_TABLE_NAME.value] = self.selectTableNameEntries[i].get()
            insertDataMap[d.InsertParam.SELECT_COLUMN_NAME.value] = self.selectColumnNameEntries[i].get()
            insertDataMap[d.InsertParam.ENUM_NAME.value] = self.enumNameComboboxes[i].get()
            insertDataMap[d.InsertParam.FIX_PARAM.value] = self.fixParamEntries[i].get()
            insertDataMap[d.InsertParam.SERIAL_START_NUMBER.value] = self.serialStartNumberEntries[i].get()
            insertDataMap[d.InsertParam.IS_NULL_ABLE.value] = self.isNullBoolList[i].get()
            insertDataMap[d.InsertParam.IS_BLANK_ABLE.value] = self.isBlankBoolList[i].get()
            insertDataMap[d.InsertParam.NEED_QUOTE.value] = self.needQuoteBoolList[i].get()
    
            insertDataMapList.append(insertDataMap)
        
        return q.createQuery(insertTableName, insertRecordLength, insertDataMapList)
    

if __name__ == "__main__":
    app = App()
    app.mainloop()