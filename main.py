#coding: utf-8
import tkinter as tk
from tkinter import ttk
import configparser
from tkinter import filedialog
from tkinter import messagebox
import os
import mysql.connector
from mysql.connector import errorcode
from enum import Enum
import random

# inputData
insertTableName = ""
insertDataMapList = []
insertRecordLength = 0

# dataMap Param enum for insert
class InsertParam(Enum):
    COLUMN_INDEX = "columnIndex"
    INSERT_COLUMN_NAME = "insertColumnName"
    DATA_TYPE = "dataType"
    SELECT_TABLE_NAME = "selectTableName"
    SELECT_COLUMN_NAME = "selectColumnName"
    ENUM_NAME = "enumName"
    FIX_PARAM = "fixParam"
    SERIAL_START_NUMBER = "serialStartNumber"
    IS_NULL_ABLE = "isNullAble"
    IS_BLANK_ABLE = "isBlankAble"
    NEED_QUOTE = "needQuote"

# dataType enum for insert
class InsertDataType(Enum):
    TABLE = "table" # or MASTER?
    ENUM = "enum"
    FIX = "fix"
    SERIAL_NUMBER = "serialNumber"
    
# param enum for select
class SelectParam(Enum):
    TABLE_NAME = "tableName"
    COLUMN_NAME_LIST = "columnNameList"
    SELECT_DATA = "selectData"
    RUNDOM_INDEX_LIST = "rundumIndexList"

class enumParam(Enum):
    ENUM_NAME = "enumName"
    ENUM_LIST = "enumList"
    RUNDOM_INDEX_LIST = "rundumIndexList"

class serialParam(Enum):
    INSERT_COLUMN_NAME = "insertColumnName"
    SERIAL_NUMBER_LIST = "serialNumberList"

class fixParam(Enum):
    INSERT_COLUMN_NAME = "insertColumnName"
    FIX_PARAM = "fixParam"

def generateRundumNumberList(insertRecordLength, targetList):
    rundumIndexList = []
    max = len(targetList) - 1
    for i in range(insertRecordLength):
        rundumIndexList.append(random.randint(0, max))
    return rundumIndexList

def createInsertQuery(insertTableName, insertDataMapList, insertFormat):
    insertColumn = ""
    insertColumnLength = len(insertDataMapList)
    for i, insertDataMap in enumerate(insertDataMapList):
        insertColumn += insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]
        if i != insertColumnLength - 1:
            insertColumn += ", "

    tableFormatMapListLength = len(insertFormat)
    insertValue = "("
    for i, formatMap in enumerate(insertFormat):
        for j, insertDataMap in enumerate(insertDataMapList):
            param = str(formatMap[insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]])
            if(insertDataMap[InsertParam.NEED_QUOTE.value]):
                param = "'" + param + "'"
            insertValue += param
            if j != insertColumnLength - 1:
                insertValue += ", "
        insertValue += ")"
        if i != tableFormatMapListLength - 1:
            insertValue += ", ("
    
    sql = "INSERT INTO " + insertTableName + " (" + insertColumn + ") VALUES " + insertValue + ";"
    return sql

def createInsertFormat(insertRecordLength, insertDataMapList, selectDataMapList, serialNumberMapList, fixDataMapList):
    tableFormatMapList = []
    for i in range(insertRecordLength):
        tableFormatMap = {}
        for insertDataMap in insertDataMapList:
            if (insertDataMap[InsertParam.DATA_TYPE.value] == InsertDataType.TABLE.value):
                for selectDataMap in selectDataMapList:
                    if (selectDataMap[SelectParam.TABLE_NAME.value] != insertDataMap[InsertParam.SELECT_TABLE_NAME.value]):
                        continue
                    columnNameList = selectDataMap[SelectParam.COLUMN_NAME_LIST.value]
                    for l, clumnName in enumerate(columnNameList):
                        if clumnName != insertDataMap[InsertParam.SELECT_COLUMN_NAME.value]:
                            continue
                        tableFormatMap[insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]] = selectDataMap[SelectParam.SELECT_DATA.value][selectDataMap[SelectParam.RUNDOM_INDEX_LIST.value][i]][columnNameList[l]]
                        break
            elif (insertDataMap[InsertParam.DATA_TYPE.value] == InsertDataType.SERIAL_NUMBER.value):
                for serialNumberMap in serialNumberMapList:
                    if (serialNumberMap[serialParam.INSERT_COLUMN_NAME.value] != insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]):
                        continue
                    tableFormatMap[insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]] = serialNumberMap[serialParam.SERIAL_NUMBER_LIST.value][i]
                    break
            elif (insertDataMap[InsertParam.DATA_TYPE.value] == InsertDataType.FIX.value):
                for fixDataMap in fixDataMapList:
                    if (fixDataMap[serialParam.INSERT_COLUMN_NAME.value] != insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]):
                        continue
                    tableFormatMap[insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]] = fixDataMap[fixParam.FIX_PARAM.value]
                    break
                
        tableFormatMapList.append(tableFormatMap)
    return tableFormatMapList

def selectMasterData(insertDataMapList):
    def createSelectFormat(insertDataMapList):
        selectFormat = []
        tableNameList = []
        for insertDataMap in insertDataMapList:
            if insertDataMap[InsertParam.DATA_TYPE.value] != InsertDataType.TABLE.value:
                continue
            
            selectTableName = insertDataMap[InsertParam.SELECT_TABLE_NAME.value]
            if selectTableName in tableNameList:
                index = tableNameList.index(selectTableName)
                columnNameList = list(selectFormat[index][SelectParam.COLUMN_NAME_LIST.value])
                columnNameList.append(insertDataMap[InsertParam.SELECT_COLUMN_NAME.value])
                selectFormat[index][SelectParam.COLUMN_NAME_LIST.value] = columnNameList
            else:
                tableMap = {}
                selectColumnNameList = []
                tableName = insertDataMap[InsertParam.SELECT_TABLE_NAME.value]
                tableNameList.append(tableName)
                selectColumnNameList.append(insertDataMap[InsertParam.SELECT_COLUMN_NAME.value])
                tableMap[SelectParam.TABLE_NAME.value] = tableName
                tableMap[SelectParam.COLUMN_NAME_LIST.value] = selectColumnNameList
                selectFormat.append(tableMap)
        
        return selectFormat

    def createSelectQuery(tableName, columnNameList):
        columnNameListLength = len(columnNameList)
        columnSelect = ""
        for i in range(columnNameListLength):
            columnSelect += columnNameList[i]
            if i != columnNameListLength - 1:
                columnSelect += ", "
        return ("SELECT " + columnSelect + " FROM " + tableName)
    
    cnx = None   
    cnx = mysql.connector.connect(
            user="root",
            password="root",
            host="localhost",
            database="db_example"
        )
    
    selectDataMapList = []
    selectFormat = createSelectFormat(insertDataMapList)
    for selectTableMap in selectFormat:
        tableName = selectTableMap[SelectParam.TABLE_NAME.value]
        columnNameList = selectTableMap[SelectParam.COLUMN_NAME_LIST.value]
        columnNameListLength = len(columnNameList)
        masterDataMapList = []
        
        sql = createSelectQuery(tableName, columnNameList)
        cursor = cnx.cursor()
        param = ()
        cursor.execute(sql, param)
        for record in cursor:
            masterDataMap = {}
            for j in range(columnNameListLength):
                masterDataMap[columnNameList[j]] = record[j]
                masterDataMapList.append(masterDataMap)
        selectTableMap[SelectParam.SELECT_DATA.value] = masterDataMapList
        selectTableMap[SelectParam.RUNDOM_INDEX_LIST.value] = generateRundumNumberList(insertRecordLength, masterDataMapList)
        selectDataMapList.append(selectTableMap)
    cursor.close()
    return selectDataMapList

def createEnumData(insertRecordLength, insertDataMapList):
    print()
    
def createSerialNumberData(insertRecordLength, insertDataMapList):
    serialNumberMapList = []
    for insertDataMap in insertDataMapList:
        if insertDataMap[InsertParam.DATA_TYPE.value] != InsertDataType.SERIAL_NUMBER.value:
            continue
        
        serialStartNumber = insertDataMap[InsertParam.SERIAL_START_NUMBER.value]
        serialNumberList = []
        for i in range(insertRecordLength):
            serialNumberList.append(serialStartNumber + i)
        serialNumberMap = {}
        serialNumberMap[serialParam.INSERT_COLUMN_NAME.value] = insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]
        serialNumberMap[serialParam.SERIAL_NUMBER_LIST.value] = serialNumberList 
        serialNumberMapList.append(serialNumberMap)
    return serialNumberMapList

def createFixData(insertDataMapList):
    fixParamMapList = []
    for insertDataMap in insertDataMapList:
        if insertDataMap[InsertParam.DATA_TYPE.value] != InsertDataType.FIX.value:
            continue
        fixParamMap = {}
        fixParamMap[fixParam.INSERT_COLUMN_NAME.value] = insertDataMap[InsertParam.INSERT_COLUMN_NAME.value]
        fixParamMap[fixParam.FIX_PARAM.value] = insertDataMap[InsertParam.FIX_PARAM.value]
        fixParamMapList.append(fixParamMap)
    return fixParamMapList
        
def createQuery(insertTableName, insertRecordLength, insertDataMapList):
    selectDataMapList = selectMasterData(insertDataMapList)
    serialNumberMapList = createSerialNumberData(insertRecordLength, insertDataMapList)
    fixDataMapList = createFixData(insertDataMapList)
    insertFormat = createInsertFormat(insertRecordLength, insertDataMapList, selectDataMapList, serialNumberMapList, fixDataMapList)
    insertQuery = createInsertQuery(insertTableName, insertDataMapList, insertFormat)
    return insertQuery

def saveSqlFile(insertQuery, filePath):
    def formatSqlFile(insertQuery:str):
        sqlFormat = insertQuery.replace(') VALUES ', ') \nVALUES \n')
        sqlFormat = sqlFormat.replace('), ', '), \n')
        return sqlFormat
    
    sqlFormat = formatSqlFile(insertQuery)
    if len(filePath) != 0:
        with open(filePath, "x") as file:
            file.write(sqlFormat)

def insertExecute(insertQuery): 
    cnx = None   
    cnx = mysql.connector.connect(
            user="root",
            password="root",
            host="localhost",
            database="db_example"
        )
    cursor = cnx.cursor()
    cursor.execute(insertQuery)
    cursor.close()
    
insertQuery = createQuery(insertTableName, insertRecordLength, insertDataMapList)
# saveSqlFile(insertQuery, filePath)
# insertExecute(insertQuery)