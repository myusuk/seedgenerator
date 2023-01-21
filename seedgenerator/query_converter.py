#coding: utf-8
import configparser
import os
import mysql.connector
from mysql.connector import errorcode
from enum import Enum
import random
from define import Define as d
import json

# TODO:delete format
class QueryConverter:
    def getSettingEnumMap():
        if not os.path.exists(d.Setting.SETTING_FILE_PATH.value):
            raise FileNotFoundError(d.Setting.SETTING_FILE_PATH.value + " is not exist")
        config = configparser.ConfigParser()
        config.read(d.Setting.SETTING_FILE_PATH.value)
        
        return map(lambda x:x[0], config.items(d.Setting.ENUM.value))
    
    def createQuery(insertTableName, insertRecordLength, insertDataMapList):
        if not os.path.exists(d.Setting.SETTING_FILE_PATH.value):
            raise FileNotFoundError(d.Setting.SETTING_FILE_PATH.value + " is not exist")
        
        config = configparser.ConfigParser()
        config.read(d.Setting.SETTING_FILE_PATH.value)
        
        HOST = config[d.Setting.DATABASE.value][d.DatabaseSetting.HOST.value]
        SCHEMA = config[d.Setting.DATABASE.value][d.DatabaseSetting.SCHEMA.value]
        USER = config[d.Setting.DATABASE.value][d.DatabaseSetting.USER.value]
        PASSWORD = config[d.Setting.DATABASE.value][d.DatabaseSetting.PASSWARD.value]
        
        NOT_QUOTE_LIST = json.loads(config[d.Setting.COMMON.value][d.CommonSetting.NOT_QUOTE_LIST.value])
        
        def generateRundumNumberList(insertRecordLength, targetList):
            rundumIndexList = []
            max = len(targetList) - 1
            for i in range(insertRecordLength):
                rundumIndexList.append(random.randint(0, max))
            return rundumIndexList
        
        def addQuote(value):
            if value in NOT_QUOTE_LIST:
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

        def createInsertFormat(insertRecordLength, insertDataMapList, selectDataMapList, enumMapList, serialNumberMapList, fixDataMapList):
            tableFormatMapList = []
            for i in range(insertRecordLength):
                tableFormatMap = {}
                for insertDataMap in insertDataMapList:
                    # master data
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
                    # enum
                    elif (insertDataMap[d.InsertParam.DATA_TYPE.value] == d.InsertDataType.ENUM.value):
                        for enumMap in enumMapList:
                            if (enumMap[d.EnumParam.ENUM_NAME.value] != insertDataMap[d.InsertParam.ENUM_NAME.value]):
                                continue
                            tableFormatMap[insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]] = enumMap[d.EnumParam.ENUM_LIST.value][enumMap[d.EnumParam.RUNDOM_INDEX_LIST.value][i]]
                            break
                    # serial number
                    elif (insertDataMap[d.InsertParam.DATA_TYPE.value] == d.InsertDataType.SERIAL_NUMBER.value):
                        for serialNumberMap in serialNumberMapList:
                            if (serialNumberMap[d.SerialParam.INSERT_COLUMN_NAME.value] != insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]):
                                continue
                            tableFormatMap[insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]] = serialNumberMap[d.SerialParam.SERIAL_NUMBER_LIST.value][i]
                            break
                    # fix param
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

        def selectMasterData(insertRecordLength, insertDataMapList):
            cnx = None   
            cnx = mysql.connector.connect(
                    user=USER,
                    password=PASSWORD,
                    host=HOST,
                    database=SCHEMA
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
                            nullMap[columnName] = "NULL"
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
            enumMapList = []
            for insertDataMap in insertDataMapList:
                if insertDataMap[d.InsertParam.DATA_TYPE.value] != d.InsertDataType.ENUM.value:
                    continue
                enumMap = {}
                enumList = json.loads(config[d.Setting.ENUM.value][insertDataMap[d.InsertParam.ENUM_NAME.value]])
                if insertDataMap[d.InsertParam.IS_NULL_ABLE.value]:
                    enumList.append("NULL")
                if insertDataMap[d.InsertParam.IS_BLANK_ABLE.value]:
                    enumList.append("''")
                enumMap[d.EnumParam.ENUM_NAME.value] = insertDataMap[d.InsertParam.ENUM_NAME.value]
                enumMap[d.EnumParam.ENUM_LIST.value] = enumList
                enumMap[d.EnumParam.RUNDOM_INDEX_LIST.value] = generateRundumNumberList(insertRecordLength, enumList)
                enumMapList.append(enumMap)
            return enumMapList
            
        def createSerialNumberData(insertRecordLength, insertDataMapList):
            serialNumberMapList = []
            for insertDataMap in insertDataMapList:
                if insertDataMap[d.InsertParam.DATA_TYPE.value] != d.InsertDataType.SERIAL_NUMBER.value:
                    continue
                
                serialStartNumber = int(insertDataMap[d.InsertParam.SERIAL_START_NUMBER.value])
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
                    fixParamList.append("NULL")
                if insertDataMap[d.InsertParam.IS_BLANK_ABLE.value]:
                    fixParamList.append("''")
                fixParamMap[d.FixParam.INSERT_COLUMN_NAME.value] = insertDataMap[d.InsertParam.INSERT_COLUMN_NAME.value]
                fixParamMap[d.FixParam.FIX_PARAM_LIST.value] = fixParamList
                fixParamMap[d.FixParam.RUNDOM_INDEX_LIST.value] = generateRundumNumberList(insertRecordLength, fixParamList)
                fixParamMapList.append(fixParamMap)
            return fixParamMapList
            
        selectDataMapList = selectMasterData(insertRecordLength, insertDataMapList)
        enumMapList = createEnumData(insertRecordLength, insertDataMapList)
        serialNumberMapList = createSerialNumberData(insertRecordLength, insertDataMapList)
        fixDataMapList = createFixData(insertRecordLength, insertDataMapList)
        insertFormat = createInsertFormat(insertRecordLength, insertDataMapList, selectDataMapList, enumMapList, serialNumberMapList, fixDataMapList)
        insertQuery = createInsertQuery(insertTableName, insertDataMapList, insertFormat)
        return insertQuery

    def saveSqlFile(insertQuery, filePath):
        sqlFormat = insertQuery.replace(") VALUES ", ") \nVALUES \n")
        sqlFormat = sqlFormat.replace("), ", "), \n")
        
        if len(filePath) != 0:
            with open(filePath, "x") as file:
                file.write(sqlFormat)

    def insertExecute(insertQuery): 
        if not os.path.exists(d.Setting.SETTING_FILE_PATH.value):
            raise FileNotFoundError(d.Setting.SETTING_FILE_PATH.value + " is not exist")
        
        config = configparser.ConfigParser()
        config.read(d.Setting.SETTING_FILE_PATH.value)
        
        HOST = config[d.Setting.DATABASE.value][d.DatabaseSetting.HOST.value]
        SCHEMA = config[d.Setting.DATABASE.value][d.DatabaseSetting.SCHEMA.value]
        USER = config[d.Setting.DATABASE.value][d.DatabaseSetting.USER.value]
        PASSWORD = config[d.Setting.DATABASE.value][d.DatabaseSetting.PASSWARD.value]
        cnx = None   
        cnx = mysql.connector.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                database=SCHEMA
            )
        cursor = cnx.cursor()
        cursor.execute(insertQuery)
        cursor.close()
    
    def settingDatabaseConfig(host, schema, username, password):
        if not os.path.exists(d.Setting.SETTING_FILE_PATH.value):
            raise FileNotFoundError(d.Setting.SETTING_FILE_PATH.value + " is not exist")
        
        config = configparser.ConfigParser()
        config.read(d.Setting.SETTING_FILE_PATH.value)
        config.set(d.Setting.DATABASE.value, d.DatabaseSetting.HOST.value, host)
        config.set(d.Setting.DATABASE.value, d.DatabaseSetting.SCHEMA.value, schema)
        config.set(d.Setting.DATABASE.value, d.DatabaseSetting.USER.value, username)
        config.set(d.Setting.DATABASE.value, d.DatabaseSetting.PASSWARD.value, password)
        
        with open(d.Setting.SETTING_FILE_PATH.value, "w") as file:
            config.write(file)

    def settingEnumConfig(targetEnumName, editEnumName, enumParamList):
        if not os.path.exists(d.Setting.SETTING_FILE_PATH.value):
            raise FileNotFoundError(d.Setting.SETTING_FILE_PATH.value + " is not exist")
        
        config = configparser.ConfigParser()
        config.read(d.Setting.SETTING_FILE_PATH.value)
        if targetEnumName != "New":
            config.remove_option(d.Setting.ENUM.value, targetEnumName)
        config.set(d.Setting.ENUM.value, editEnumName, str(enumParamList))
        
        
        with open(d.Setting.SETTING_FILE_PATH.value, "w") as file:
            config.write(file)
    