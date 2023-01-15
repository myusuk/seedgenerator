#coding: utf-8
import configparser
import os
import mysql.connector
from mysql.connector import errorcode
from enum import Enum
import random
from define import Define as d

# TODO:delete format
class QueryConverter:
    def createQuery(insertTableName, insertRecordLength, insertDataMapList):
        def generateRundumNumberList(insertRecordLength, targetList):
            rundumIndexList = []
            max = len(targetList) - 1
            for i in range(insertRecordLength):
                rundumIndexList.append(random.randint(0, max))
            return rundumIndexList
        
        def addQuote(value):
            notQuoteList = ["NULL", "''"]
            if value in notQuoteList:
                return value
            value = "'" + value + "'"
            return value

        def createInsertQuery(insertTableName, insertDataMapList, insertFormat):
            insertColumn = ""
            insertColumnLength = len(insertDataMapList)
            for i, insertDataMap in enumerate(insertDataMapList):
                insertColumn += insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]
                if i != insertColumnLength - 1:
                    insertColumn += ", "

            tableFormatMapListLength = len(insertFormat)
            insertValue = "("
            for i, formatMap in enumerate(insertFormat):
                for j, insertDataMap in enumerate(insertDataMapList):
                    param = str(formatMap[insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]])
                    if(insertDataMap[d.InsertParam.NEED_QUOTE.value]):
                        param = addQuote(param)
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
                    if (insertDataMap[d.InsertParam.DATA_TYPE.value] == d.InsertDataType.TABLE.value):
                        for selectDataMap in selectDataMapList:
                            if (selectDataMap[d.SelectParam.TABLE_NAME.value] != insertDataMap[d.InsertParam.SELECT_TABLE_NAME.value]):
                                continue
                            columnNameList = selectDataMap[d.SelectParam.COLUMN_NAME_LIST.value]
                            for l, clumnName in enumerate(columnNameList):
                                if clumnName != insertDataMap[d.InsertParam.SELECT_COLUMN_NAME.value]:
                                    continue
                                tableFormatMap[insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]] = selectDataMap[d.SelectParam.SELECT_DATA.value][selectDataMap[d.SelectParam.RUNDOM_INDEX_LIST.value][i]][columnNameList[l]]
                                break
                    elif (insertDataMap[d.InsertParam.DATA_TYPE.value] == d.InsertDataType.SERIAL_NUMBER.value):
                        for serialNumberMap in serialNumberMapList:
                            if (serialNumberMap[d.SerialParam.INSERT_COLUMN_NAME.value] != insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]):
                                continue
                            tableFormatMap[insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]] = serialNumberMap[d.SerialParam.SERIAL_NUMBER_LIST.value][i]
                            break
                    elif (insertDataMap[d.InsertParam.DATA_TYPE.value] == d.InsertDataType.FIX.value):
                        for fixDataMap in fixDataMapList:
                            if (fixDataMap[d.SerialParam.INSERT_COLUMN_NAME.value] != insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]):
                                continue
                            tableFormatMap[insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]] = fixDataMap[d.FixParam.FIX_PARAM_LIST.value][fixDataMap[d.FixParam.RUNDOM_INDEX_LIST.value][i]]
                            break
                        
                tableFormatMapList.append(tableFormatMap)
            return tableFormatMapList

        def createSelectFormat(insertDataMapList):
            selectFormat = []
            tableNameList = []
            for insertDataMap in insertDataMapList:
                if insertDataMap[d.InsertParam.DATA_TYPE.value] != d.InsertDataType.TABLE.value:
                    continue
                    
                selectTableName = insertDataMap[d.InsertParam.SELECT_TABLE_NAME.value]
                if selectTableName not in tableNameList:
                    tableMap = {}
                    selectColumnNameList = []
                    isNullAbleList = []
                    isBlankAbleList = []
                    tableName = insertDataMap[d.InsertParam.SELECT_TABLE_NAME.value]
                    selectColumnNameList.append(insertDataMap[d.InsertParam.SELECT_COLUMN_NAME.value])
                    isNullAbleList.append(insertDataMap[d.InsertParam.IS_NULL_ABLE.value])
                    isBlankAbleList.append(insertDataMap[d.InsertParam.IS_BLANK_ABLE.value])
                    tableMap[d.SelectParam.TABLE_NAME.value] = tableName
                    tableMap[d.SelectParam.COLUMN_NAME_LIST.value] = selectColumnNameList
                    tableMap[d.SelectParam.NULL_ABLE_LIST.value] = isNullAbleList
                    tableMap[d.SelectParam.BLANK_ABLE_LIST.value] = isBlankAbleList
                    selectFormat.append(tableMap)
                    tableNameList.append(tableName)
                else:
                    index = tableNameList.index(selectTableName)
                    columnNameList = list(selectFormat[index][d.SelectParam.COLUMN_NAME_LIST.value])
                    columnNameList.append(insertDataMap[d.InsertParam.SELECT_COLUMN_NAME.value])
                    selectFormat[index][d.SelectParam.COLUMN_NAME_LIST.value] = columnNameList
                    isNullAbleList = list(selectFormat[index][d.SelectParam.NULL_ABLE_LIST.value])
                    isNullAbleList.append(insertDataMap[d.InsertParam.IS_NULL_ABLE.value])
                    selectFormat[index][d.SelectParam.NULL_ABLE_LIST.value] = isNullAbleList
                    isBlankAbleList = list(selectFormat[index][d.SelectParam.BLANK_ABLE_LIST.value])
                    isBlankAbleList.append(insertDataMap[d.InsertParam.IS_BLANK_ABLE.value])
                    selectFormat[index][d.SelectParam.BLANK_ABLE_LIST.value] = isBlankAbleList
                
            return selectFormat

        def createSelectQuery(tableName, columnNameList):
            columnNameListLength = len(columnNameList)
            columnSelect = ""
            for i in range(columnNameListLength):
                columnSelect += columnNameList[i]
                if i != columnNameListLength - 1:
                    columnSelect += ", "
            return ("SELECT " + columnSelect + " FROM " + tableName)

        def selectMasterData(insertDataMapList):
            cnx = None   
            cnx = mysql.connector.connect(
                    user="root",
                    password="root",
                    host="localhost",
                    database="db_example"
                )
            cursor = cnx.cursor()
            
            selectDataMapList = []
            selectFormat = createSelectFormat(insertDataMapList)
            for selectTableMap in selectFormat:
                tableName = selectTableMap[d.SelectParam.TABLE_NAME.value]
                columnNameList = selectTableMap[d.SelectParam.COLUMN_NAME_LIST.value]
                columnNameListLength = len(columnNameList)
                masterDataMapList = []
                
                sql = createSelectQuery(tableName, columnNameList)
                
                param = ()
                cursor.execute(sql, param)
                for record in cursor:
                    masterDataMap = {}
                    for j in range(columnNameListLength):
                        masterDataMap[columnNameList[j]] = record[j]
                        masterDataMapList.append(masterDataMap)
                
                nullFlg = True in selectTableMap[d.SelectParam.NULL_ABLE_LIST.value]
                blankFlg = True in selectTableMap[d.SelectParam.BLANK_ABLE_LIST.value]
                if nullFlg:
                    nullMap = {}
                    otherIndex = random.randint(0, columnNameListLength)
                    for i, columnName in enumerate(columnNameList):
                        if selectTableMap[d.SelectParam.NULL_ABLE_LIST.value][i]:
                            nullMap[columnName] = 'NULL'
                        else:
                            nullMap[columnName] = masterDataMapList[otherIndex][columnName]
                    masterDataMapList.append(nullMap)
                
                if blankFlg:
                    blankMap = {}
                    otherIndex = random.randint(0, columnNameListLength)
                    for i, columnName in enumerate(columnNameList):
                        if selectTableMap[d.SelectParam.BLANK_ABLE_LIST.value][i]:
                            blankMap[columnName] = "''"
                        else:
                            blankMap[columnName] = masterDataMapList[otherIndex][columnName]
                    masterDataMapList.append(blankMap)
                
                selectTableMap[d.SelectParam.SELECT_DATA.value] = masterDataMapList
                selectTableMap[d.SelectParam.RUNDOM_INDEX_LIST.value] = generateRundumNumberList(insertRecordLength, masterDataMapList)
                selectDataMapList.append(selectTableMap)
            cursor.close()
            return selectDataMapList

        def createEnumData(insertRecordLength, insertDataMapList):
            print()
            
        def createSerialNumberData(insertRecordLength, insertDataMapList):
            serialNumberMapList = []
            for insertDataMap in insertDataMapList:
                if insertDataMap[d.InsertParam.DATA_TYPE.value] != d.InsertDataType.SERIAL_NUMBER.value:
                    continue
                
                serialStartNumber = insertDataMap[d.InsertParam.SERIAL_START_NUMBER.value]
                serialNumberList = []
                for i in range(insertRecordLength):
                    serialNumberList.append(serialStartNumber + i)
                serialNumberMap = {}
                serialNumberMap[d.SerialParam.INSERT_COLUMN_NAME.value] = insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]
                serialNumberMap[d.SerialParam.SERIAL_NUMBER_LIST.value] = serialNumberList 
                serialNumberMapList.append(serialNumberMap)
            return serialNumberMapList

        def createFixData(insertRecordLength, insertDataMapList):
            fixParamMapList = []
            for insertDataMap in insertDataMapList:
                if insertDataMap[d.InsertParam.DATA_TYPE.value] != d.InsertDataType.FIX.value:
                    continue
                fixParamMap = {}
                fixParamList = []
                fixParamList.append(insertDataMap[d.InsertParam.FIX_PARAM.value])
                if insertDataMap[d.InsertParam.IS_NULL_ABLE.value]:
                    fixParamList.append('NULL')
                if insertDataMap[d.InsertParam.IS_BLANK_ABLE.value]:
                    fixParamList.append('')
                fixParamMap[d.FixParam.INSERT_COLUMN_NAME.value] = insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]
                fixParamMap[d.FixParam.FIX_PARAM_LIST.value] = fixParamList
                fixParamMap[d.FixParam.RUNDOM_INDEX_LIST.value] = generateRundumNumberList(insertRecordLength, fixParamList)
                fixParamMapList.append(fixParamMap)
            return fixParamMapList
            
        selectDataMapList = selectMasterData(insertDataMapList)
        serialNumberMapList = createSerialNumberData(insertRecordLength, insertDataMapList)
        fixDataMapList = createFixData(insertRecordLength, insertDataMapList)
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
    