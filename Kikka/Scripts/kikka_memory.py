# coding=utf-8
import os
import sqlite3
import json
import logging

import binascii
import sys
import random
import base64

from sympy import nextprime
from struct import pack
from Crypto.Cipher import AES

import kikka
import kikka_const


class KikkaMemory:
    _instance = None
    isDebug = False

    def __init__(self, **kwargs):
        raise SyntaxError('KikkaMemory has only one, please use KikkaMemory.this()')

    @staticmethod
    def this():
        if KikkaMemory._instance is None:
            KikkaMemory._instance = object.__new__(KikkaMemory)
            KikkaMemory._instance._init()
        return KikkaMemory._instance

    def _init(self):
        self._deepmemory = None
        self._filepath = None

    def awake(self, filename):
        if self._deepmemory is not None:
            self._deepmemory.close()

        self._filepath = filename
        memoryEsists = os.path.exists(filename)
        self._sql_worker = Sqlite3Worker(filename)

        if memoryEsists:
            # create new database
            logging.info("awake kikka memory")

        logging.info("linked kikka memory")

    def close(self):
        if self._sql_worker is not None:
            self._sql_worker.close()
            self._sql_worker = None


    def createTable(self, table_name):
        try:
            name = str('T_' + table_name).upper()
            sql = "create table if not exists %s(key text not null, soul integer not null, value text, primary key (key, soul))"%name
            self._sql_worker.execute(sql)
        except ValueError:
            logging.warning('read table memory fail: key[%s]' % table_name)

    def read(self, table_name, key, default='', soulID=0):
        logging.debug("kikka memory read %s"%key)
        try:
            name = str('T_' + table_name).upper()
            sql = "select value from %s where key=? and soul=?" % name

            result = self._sql_worker.execute(sql, (key, soulID))
            if len(result) != 0:
                value = result[0][0]
            else:
                return default

            if isinstance(default, str) is True: return str(value)
            elif isinstance(default, bool) is True: return value == 'True'
            elif isinstance(default, int) is True: return int(value)
            elif isinstance(default, float) is True: return float(value)
            elif isinstance(default, list) is True: return json.loads(value)
            elif isinstance(default, dict) is True: return json.loads(value)
            else: return default
        except ValueError:
            logging.warning('read memory fail: key[%s]' % key)
            return default

    def write(self, table_name, key, value, soulID=0):
        logging.debug("kikka memory write %s"%key)
        try:
            name = str('T_' + table_name).upper()
            sql = "insert or replace into %s(key, soul, value) values(?, ?, ?)" % name

            if isinstance(value, dict) is True:
                for k in value.keys():
                    if isinstance(k, (bool, int, float)) is False:
                        continue
                    logging.warning("when write dict to memory, the key of bool, int or float will be converted to string")
                    break

            value = str(value) if isinstance(value, (list, dict)) is False else json.dumps(value)
            self._sql_worker.execute(sql, (key, soulID, value))
        except Exception:
            logging.warning('write memory fail: key[%s]' % key)

    def execute(self, query, values=None):
        return self._sql_worker.execute(query, values)

class DeepMemory:
    def __init__(self, filename):
        self._sql_worker = Sqlite3Worker(filename)

    def __del__(self):
        self.close()

    def awake(self):
        pass

    def close(self):
        logging.info("__del__")

        if self._sql_worker is not None:
            self._sql_worker.close()
            self._sql_worker = None

    def createTable(self, table_name):
        try:
            name = str('T_' + table_name).upper()
            sql = "create table if not exists %s(key text not null, soul integer not null, value text, primary key (key, soul))"%name
            self._sql_worker.execute(sql)
        except ValueError:
            logging.warning('read table memory fail: key[%s]' % table_name)

    def read(self, table_name, key, default, soul=0):
        try:
            name = str('T_' + table_name).upper()
            sql = "select value from %s where key=? and soul=?" % name

            result = self._sql_worker.execute(sql, (key, soul))
            if len(result) != 0:
                value = result[0][0]
            else:
                return default

            if isinstance(default, str) is True: return str(value)
            elif isinstance(default, bool) is True: return value == 'True'
            elif isinstance(default, int) is True: return int(value)
            elif isinstance(default, float) is True: return float(value)
            elif isinstance(default, list) is True: return json.loads(value)
            elif isinstance(default, dict) is True: return json.loads(value)
            else: return default
        except ValueError:
            logging.warning('read memory fail: key[%s]' % key)
            return default

    def write(self, table_name, key, value, soul=0):
        try:
            name = str('T_' + table_name).upper()
            sql = "insert or replace into %s(key, soul, value) values(?, ?, ?)" % name

            if isinstance(value, dict) is True:
                for k in value.keys():
                    if isinstance(k, (bool, int, float)) is False:
                        continue
                    logging.warning("when write dict to memory, the key of bool, int or float will be converted to string")
                    break

            value = str(value) if isinstance(value, (list, dict)) is False else json.dumps(value)
            self._sql_worker.execute(sql, (key, soul, value))
        except Exception:
            logging.warning('write memory fail: key[%s]' % key)

    def execute(self, query, values=None):
        return self._sql_worker.execute(query, values)


# ###########################################################################################################
# Copyright (c) 2014 Palantir Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# """Thread safe sqlite3 interface."""
#
# __author__ = "Shawn Lee"
# __email__ = "shawnl@palantir.com"
# __license__ = "MIT"

import logging
import queue
import sqlite3
import threading
import time
import uuid

class Sqlite3Worker(threading.Thread):
    """Sqlite thread safe object.
    Example:
        from sqlite3worker import Sqlite3Worker
        sql_worker = Sqlite3Worker("/tmp/test.sqlite")
        sql_worker.execute(
            "CREATE TABLE tester (timestamp DATETIME, uuid TEXT)")
        sql_worker.execute(
            "INSERT into tester values (?, ?)", ("2010-01-01 13:00:00", "bow"))
        sql_worker.execute(
            "INSERT into tester values (?, ?)", ("2011-02-02 14:14:14", "dog"))
        sql_worker.execute("SELECT * from tester")
        sql_worker.close()
    """
    def __init__(self, file_name, max_queue_size=100):
        """Automatically starts the thread.
        Args:
            file_name: The name of the file.
            max_queue_size: The max queries that will be queued.
        """
        threading.Thread.__init__(self)
        self.daemon = True
        self.sqlite3_conn = sqlite3.connect(file_name, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
        self.sqlite3_cursor = self.sqlite3_conn.cursor()
        self.sql_queue = queue.Queue(maxsize=max_queue_size)
        self.results = {}
        self.max_queue_size = max_queue_size
        self.exit_set = False
        # Token that is put into queue when close() is called.
        self.exit_token = str(uuid.uuid4())
        self.start()
        self.thread_running = True

    def run(self):
        """Thread loop.
        This is an infinite loop.  The iter method calls self.sql_queue.get()
        which blocks if there are not values in the queue.  As soon as values
        are placed into the queue the process will continue.
        If many executes happen at once it will churn through them all before
        calling commit() to speed things up by reducing the number of times
        commit is called.
        """
        logging.debug("run: Thread started")
        execute_count = 0
        for token, query, values in iter(self.sql_queue.get, None):
            logging.debug("sql_queue: %s", self.sql_queue.qsize())
            if token != self.exit_token:
                logging.debug("run: %s", query)
                self.run_query(token, query, values)
                execute_count += 1
                # Let the executes build up a little before committing to disk
                # to speed things up.
                if self.sql_queue.empty() \
                or execute_count == self.max_queue_size:
                    logging.debug("run: commit")
                    self.sqlite3_conn.commit()
                    execute_count = 0
            pass # exit if

            # Only exit if the queue is empty. Otherwise keep getting
            # through the queue until it's empty.
            if self.exit_set and self.sql_queue.empty():
                self.sqlite3_conn.commit()
                self.sqlite3_conn.close()
                self.thread_running = False
                return
        pass

    def run_query(self, token, query, values):
        """Run a query.
        Args:
            token: A uuid object of the query you want returned.
            query: A sql query with ? placeholders for values.
            values: A tuple of values to replace "?" in query.
        """
        if query.lower().strip().startswith("select"):
            try:
                self.sqlite3_cursor.execute(query, values)
                self.results[token] = self.sqlite3_cursor.fetchall()
            except sqlite3.Error as err:
                # Put the error into the output queue since a response
                # is required.
                self.results[token] = ("Query returned error: %s: %s: %s" % (query, values, err))
                logging.error("Query returned error: %s: %s: %s", query, values, err)
            pass
        else:
            try:
                self.sqlite3_cursor.execute(query, values)
            except sqlite3.Error as err:
                logging.error(
                    "Query returned error: %s: %s: %s", query, values, err)
        pass

    def close(self):
        """Close down the thread and close the sqlite3 database file."""
        self.exit_set = True
        self.sql_queue.put((self.exit_token, "", ""), timeout=5)
        # Sleep and check that the thread is done before returning.
        while self.thread_running:
            time.sleep(.01)  # Don't kill the CPU waiting.

    @property
    def queue_size(self):
        """Return the queue size."""
        return self.sql_queue.qsize()

    def query_results(self, token):
        """Get the query results for a specific token.
        Args:
            token: A uuid object of the query you want returned.
        Returns:
            Return the results of the query when it's executed by the thread.
        """
        delay = .001
        while True:
            if token in self.results:
                return_val = self.results[token]
                del self.results[token]
                return return_val
            # Double back on the delay to a max of 8 seconds.  This prevents
            # a long lived select statement from trashing the CPU with this
            # infinite loop as it's waiting for the query results.
            logging.debug("Sleeping: %s %s", delay, token)
            time.sleep(delay)
            if delay < 8:
                delay += delay
        pass

    def execute(self, query, values=None):
        """Execute a query.
        Args:
            query: The sql string using ? for placeholders of dynamic values.
            values: A tuple of values to be replaced into the ? of the query.
        Returns:
            If it's a select query it will return the results of the query.
        """
        if self.exit_set:
            logging.debug("Exit set, not running: %s", query)
            return "Exit Called"
        logging.debug("execute: %s", query)
        values = values or []
        # A token to track this query with.
        token = str(uuid.uuid4())
        # If it's a select we queue it up with a token to mark the results
        # into the output queue so we know what results are ours.
        if query.lower().strip().startswith("select"):
            self.sql_queue.put((token, query, values), timeout=5)
            return self.query_results(token)
        else:
            self.sql_queue.put((token, query, values), timeout=5)

    pass
