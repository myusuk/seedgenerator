from enum import Enum

class Define:
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
        
        def getInsertParamList():
            print()

    # dataType enum for insert
    class InsertDataType(Enum):
        TABLE = "table"
        ENUM = "enum"
        FIX = "fix"
        SERIAL_NUMBER = "serialNumber"
        
    # param enum for select
    class SelectParam(Enum):
        TABLE_NAME = "tableName"
        COLUMN_NAME_LIST = "columnNameList"
        SELECT_DATA = "selectData"
        NULL_ABLE_LIST = "nullAbleList" # need map?
        BLANK_ABLE_LIST = "blankAbleList" # need map?
        RUNDOM_INDEX_LIST = "rundumIndexList"

    class EnumParam(Enum):
        ENUM_NAME = "enumName"
        ENUM_LIST = "enumList"
        RUNDOM_INDEX_LIST = "rundumIndexList"

    class SerialParam(Enum):
        INSERT_COLUMN_NAME = "insertColumnName"
        SERIAL_NUMBER_LIST = "serialNumberList"

    class FixParam(Enum):
        INSERT_COLUMN_NAME = "insertColumnName"
        FIX_PARAM_LIST = "fixParam" # contain null blank
        RUNDOM_INDEX_LIST = "rundumIndexList"