import os
import sqlite3


class KikkaMemory(object):
    _instance = None

    def __init__(self, **kwargs):
        raise SyntaxError('KikkaMemory has only one, please use KikkaMemory.this()')

    def __del__(self):
        self._cursor.close()
        self._conn.close()

    def this():
        if KikkaMemory._instance is None:
            KikkaMemory._instance = object.__new__(KikkaMemory)
            KikkaMemory._instance._init()
        return KikkaMemory._instance

    def _init(self):
        self._filepath = 'Kikka.Memory'
        if os.path.exists(self._filepath) != True:
            self._createDB()
        else:
            self._openDB()

        #self._update('key', 'kikka99988')
        #print(self.getValue('key'))

        pass

    def _createDB(self):
        self._conn = sqlite3.connect(self._filepath)
        self._cursor = self._conn.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS T_DICT(__key__ text, __value__ text)'
        self._cursor.execute(sql)
        self._conn.commit()

    def _openDB(self):
        self._conn = sqlite3.connect(self._filepath)
        self._cursor = self._conn.cursor()

    def _query(self, sql):
        return self._cursor.execute(sql)

    def setValue(self, key, value):
        if self.getValue(key) != None:
            sql = 'UPDATE T_DICT SET __value__=? WHERE __key__=?'
            values = (str(value), str(key))
        else:
            sql = 'INSERT INTO T_DICT values(?,?)'
            values = (str(key), str(value))

        self._cursor.execute(sql, values)
        self._conn.commit()

    def getValue(self, key):
        sql = 'SELECT __value__ FROM T_DICT WHERE __key__=?'
        result = self._cursor.execute(sql, [key])
        f= result.fetchall()

        if len(f) == 0: return None
        else: return f[0][0]
