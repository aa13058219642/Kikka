# coding=utf-8
import os
import sqlite3
import json
import logging


class KikkaMemory:
    _instance = None

    def __init__(self, **kwargs):
        raise SyntaxError('KikkaMemory has only one, please use KikkaMemory.this()')

    def __del__(self):
        self.close()

    @staticmethod
    def this():
        if KikkaMemory._instance is None:
            KikkaMemory._instance = object.__new__(KikkaMemory)
            KikkaMemory._instance._init()
        return KikkaMemory._instance

    def _init(self):
        self._filepath = 'Kikka.Memory'
        if not os.path.exists(self._filepath):
            self._createDB()
        else:
            self._openDB()
        pass

    def close(self):
        self._cursor.close()
        self._conn.close()

    def _openDB(self):
        self._conn = sqlite3.connect(self._filepath)
        self._cursor = self._conn.cursor()
        logging.info("inited kikka memory")

    def _query(self, sql):
        return self._cursor.execute(sql)

    def set(self, key, value, systemkey=False):
        old_value = self.getString(key, None, systemkey)
        if old_value is not None:
            if old_value == value: return

            if systemkey is True: key = "__%s__" % key
            sql = 'insert or replace into T_DICT(__KEY__, __VALUE__) values(?, ?)'
            parameter = [str(key), str(value)]
            self._cursor.execute(sql, parameter)
            self._conn.commit()

    def getString(self, key, default=None, systemkey=False):
        result = default

        if systemkey is True: key = "__%s__" % key
        sql = 'select __VALUE__ from T_DICT where __KEY__=?'
        sql_result = self._cursor.execute(sql, [key])
        f = sql_result.fetchall()
        if len(f) != 0: result = f[0][0]

        return result

    def getInteger(self, key, default=0, systemkey=False):
        return int(self.getString(key, default, systemkey))

    def _createDB(self):
        self._conn = sqlite3.connect(self._filepath)
        self._cursor = self._conn.cursor()
        sql = 'create table if not exists T_DICT(__KEY__ text primary key not null, __VALUE__ text)'
        self._cursor.execute(sql)

        data = self._getDefautData()
        sql = 'insert into T_DICT(__KEY__, __VALUE__) values(?, ?)'
        self._conn.executemany(sql, data)
        self._conn.commit()
        logging.info("crated kikka memory")

    def _getDefautData(self):
        s = '''
        {
            "__Version__":"1.0.0",
            "__Author__": "A.A",
            "__CurShell__": 1
        }
        '''
        j = json.loads(s)

        s = {}
        for k, v in j.items():
            s[str(k)] = str(v)

        parameters = []
        for k, v in s.items():
            parameters.append((str(k), str(v)))
        return parameters
